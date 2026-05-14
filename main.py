"""
ClearPass — Main FastAPI Application (Layer 5: Orchestrator)
=============================================================
Portable KYC and AI trust-scoring API. Orchestrates biometric
face matching, financial feature extraction, three parallel ML
models, and a weighted trust-score assembler behind a single
POST /verify endpoint.

All models are trained/loaded at startup. Redis caching avoids
redundant re-computation within a 6-hour window.
"""

import asyncio
import logging
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-30s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("clearpass.main")

# ---------------------------------------------------------------------------
# Lazy Loading Helpers
# ---------------------------------------------------------------------------
logger.info("=== ClearPass starting (Lazy Loading Mode) ===")

# We move heavy imports inside functions to prevent Render startup timeouts.
# Models will load on first use.

# ---------------------------------------------------------------------------
# Background Warmup
# ---------------------------------------------------------------------------
import threading

MODELS_LOADED = False

def warmup_models():
    """Load heavy models in a background thread to avoid startup timeouts."""
    global MODELS_LOADED
    try:
        logger.info("=== Background Warmup: Loading AI models... ===")
        from services.face_match import match_faces
        from services.model_a_behavior import score_behavior
        from services.model_b_anomaly import detect_anomaly
        from services.model_c_graph import add_user_to_graph
        from services.cache import get_cached_verdict
        from services.db import get_verification
        MODELS_LOADED = True
        logger.info("=== Background Warmup: All models loaded successfully! ===")
    except Exception as e:
        logger.error(f"=== Background Warmup FAILED: {e} ===")

# Start warmup immediately
threading.Thread(target=warmup_models, daemon=True).start()

# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="ClearPass AI",
    description="Portable KYC & AI Trust-Scoring Infrastructure",
    version="1.0.0",
)

# CORS — allow frontend on any origin during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

# Serve static assets (CSS, JS)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

_executor = ThreadPoolExecutor(max_workers=4)


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------
class Transaction(BaseModel):
    amount: float
    date: str
    status: str
    narration: str
    type: str = Field(..., pattern="^(credit|debit)$")


class VerifyRequest(BaseModel):
    bvn: str
    phone: str
    device_id: str
    address: str
    live_image_b64: str
    official_image_b64: str | None = None
    transactions: list[Transaction]
    face_match_score: float | None = None


# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception:\n%s", traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": str(type(exc).__name__)},
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/", include_in_schema=False)
async def serve_frontend():
    """Serve the ClearPass frontend UI."""
    index_path = BASE_DIR / "index.html"
    if not index_path.exists():
        # Fallback to static if not found in root
        index_path = STATIC_DIR / "index.html"
    
    if not index_path.exists():
        logger.error(f"Frontend file missing at both root and static: {index_path}")
        return JSONResponse(
            status_code=404, 
            content={"detail": "Frontend index.html not found. Check deployment structure."}
        )
    return FileResponse(index_path)


@app.get("/health")
async def health_check():
    """Liveness / readiness probe."""
    return {
        "status": "ok", 
        "models_ready": MODELS_LOADED, 
        "cwd": os.getcwd(),
        "static_exists": STATIC_DIR.exists()
    }

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(STATIC_DIR / "favicon.ico") if (STATIC_DIR / "favicon.ico").exists() else JSONResponse(status_code=204, content=None)

@app.get("/dashboard", include_in_schema=False)
async def serve_dashboard():
    """Serve the ClearPass Developer Dashboard."""
    dash_path = STATIC_DIR / "dashboard.html"
    if not dash_path.exists():
        return JSONResponse(status_code=404, content={"detail": "Dashboard file missing"})
    return FileResponse(dash_path)

@app.get("/api/identity/check/{bvn}")
async def check_identity(bvn: str):
    """
    Identity Search: Checks if a user is already tokenized in the network.
    Part of the 'Verify Once, Use Everywhere' vision.
    """
    from services.db import get_verification
    record = get_verification(bvn)
    if record:
        return {
            "found": True,
            "trust_score": record["trust_score"],
            "verdict": record["verdict"],
            "timestamp": record.get("timestamp")
        }
    return {"found": False}

@app.get("/api/logs")
async def get_logs():
    """Fetch recent verifications for the developer console."""
    from services.db import get_recent_verifications
    return {"logs": get_recent_verifications(50)}

class MonoAuth(BaseModel):
    auth_code: str

@app.post("/api/mono/exchange")
async def mono_exchange(payload: MonoAuth):
    """Real Mono integration flow: Auth code -> Transactions."""
    from services.mono import MonoService
    transactions = await MonoService.exchange_auth_code(payload.auth_code)
    return {"transactions": transactions}


class PayoutRequest(BaseModel):
    bvn: str
    amount: float
    account_number: str

@app.post("/api/squad/payout")
async def squad_payout(payload: PayoutRequest):
    """
    The Causal Gate Endpoint.
    Only allows payouts if the user has a passing Trust Score.
    """
    from services.db import get_verification
    from services.squad import SquadService

    verdict = get_verification(payload.bvn)
    if not verdict:
        raise HTTPException(status_code=404, detail="Identity not verified. Run ClearPass first.")

    trust_score = verdict.get("trust_score", 0)
    
    result = await SquadService.execute_conditional_payout(
        payload.bvn, 
        payload.amount, 
        trust_score, 
        payload.account_number
    )
    
    if result["status"] == "blocked":
        raise HTTPException(status_code=403, detail=result)
        
    return result


@app.post("/verify")
async def verify(payload: VerifyRequest):
    """
    Full ClearPass KYC verification pipeline (Lazy Loading).
    """
    # Lazy imports to speed up startup
    from services.face_match import match_faces
    from services.feature_extractor import extract_features
    from services.model_a_behavior import score_behavior
    from services.model_b_anomaly import detect_anomaly
    from services.model_c_graph import add_user_to_graph, score_graph
    from services.score_assembler import assemble_trust_score
    from services.cache import get_cached_verdict, cache_verdict
    from services.db import save_verification, get_verification

    start = time.perf_counter()
    logger.info("=== /verify request for BVN %s ===", payload.bvn[:6] + "****")

    # ---- Step 1: Cache check ----
    cached = get_cached_verdict(payload.bvn)
    if not cached:
        # Fallback to persistent tokenization in SQLite
        cached = get_verification(payload.bvn)

    if cached is not None:
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        logger.info("Returning cached verdict in %.2f ms", elapsed)
        return {**cached, "cached": True, "processing_time_ms": elapsed}

    # ---- Step 2: Biometric face match ----
    if payload.face_match_score is not None:
        # High-speed lane: Use the score from the frontend
        logger.info("Using frontend biometric score: %.2f", payload.face_match_score)
        face_match_score = payload.face_match_score
        if face_match_score < 0.60: # Basic threshold for speed mode
            elapsed = round((time.perf_counter() - start) * 1000, 2)
            logger.info("Biometric mismatch (Frontend) — blocking")
            block_result = {
                "trust_score": 0,
                "verdict": "BLOCK",
                "reason": "biometric_mismatch",
                "face_match_score": face_match_score,
                "cached": False,
                "processing_time_ms": elapsed,
            }
            cache_verdict(payload.bvn, block_result)
            save_verification(payload.bvn, block_result)
            return block_result
    elif payload.official_image_b64:
        # Standard lane: Server-side match (Heavy)
        try:
            face_result = match_faces(payload.live_image_b64, payload.official_image_b64)
        except ValueError as exc:
            logger.warning("Face match failed: %s", exc)
            raise HTTPException(status_code=422, detail=str(exc))

        if not face_result["pass"]:
            elapsed = round((time.perf_counter() - start) * 1000, 2)
            logger.info("Biometric mismatch — blocking immediately")
            block_result = {
                "trust_score": 0,
                "verdict": "BLOCK",
                "reason": "biometric_mismatch",
                "face_match_score": face_result["score"],
                "cached": False,
                "processing_time_ms": elapsed,
            }
            cache_verdict(payload.bvn, block_result)
            save_verification(payload.bvn, block_result)
            return block_result
        face_match_score = face_result["score"]
    else:
        face_match_score = None

    # ---- Step 3: Feature extraction ----
    transactions_raw = [tx.model_dump() for tx in payload.transactions]
    features = extract_features(transactions_raw)

    # ---- Step 4: Parallel model scoring ----
    loop = asyncio.get_running_loop()

    # Add user to graph first (mutation, must complete before scoring)
    await loop.run_in_executor(
        _executor,
        add_user_to_graph,
        payload.bvn,
        payload.phone,
        payload.device_id,
        payload.address,
    )

    # Run all three models concurrently
    result_a, result_b, result_c = await asyncio.gather(
        loop.run_in_executor(_executor, score_behavior, features),
        loop.run_in_executor(_executor, detect_anomaly, features),
        loop.run_in_executor(_executor, score_graph, payload.bvn),
    )

    # ---- Step 5: Assemble trust score ----
    verdict = assemble_trust_score(result_a, result_b, result_c, features)

    # ---- Step 6: Build response ----
    elapsed = round((time.perf_counter() - start) * 1000, 2)

    response: dict[str, Any] = {
        **verdict,
        "face_match_score": face_match_score,
        "cached": False,
        "processing_time_ms": elapsed,
    }

    # ---- Step 7: Cache and Tokenize ----
    cache_verdict(payload.bvn, response)
    save_verification(payload.bvn, response)

    # ---- Step 8: SaaS Billing (Squad) ----
    from services.squad import SquadService
    SquadService.audit_verification(payload.bvn)

    logger.info(
        "=== /verify complete — score: %d, verdict: %s, time: %.2f ms ===",
        verdict["trust_score"],
        verdict["verdict"],
        elapsed,
    )
    return response


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")

