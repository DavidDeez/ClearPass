"""
Module 9 — Mono Open Banking Integration (Layer 4)
==================================================
Handles data exchange with the Mono API. Converts Mono's 
transactional JSON payloads into the "engineered banking signals" 
expected by the ClearPass ML models.
"""

import logging
from typing import Any, List
from services.feature_extractor import extract_features

logger = logging.getLogger("clearpass.mono")

class MonoService:
    @staticmethod
    def process_statement(mono_transactions: List[dict]) -> dict[str, float]:
        """
        Convert raw Mono transaction data into ML-ready features.
        
        Mono data usually contains 'amount', 'date', 'type', 'narration'.
        """
        logger.info("Mono: Processing %d transactions for feature extraction", len(mono_transactions))
        
        # We leverage the existing feature_extractor which is already designed
        # to handle the common transaction schema.
        try:
            features = extract_features(mono_transactions)
            logger.info("Mono: Feature extraction complete")
            return features
        except Exception as e:
            logger.error("Mono: Feature extraction failed: %s", str(e))
            raise ValueError(f"Failed to process Mono data: {e}")

    @staticmethod
    async def exchange_auth_code(auth_code: str) -> List[dict]:
        """
        Exchange a Mono auth code for a transaction statement.
        (Mocked for hackathon demonstration)
        """
        logger.info("Mono: Exchanging auth code %s...", auth_code[:5] + "***")
        
        # In a real app, this would call:
        # 1. POST /account/auth (to get account ID)
        # 2. GET /accounts/:id/statement
        
        from services.synthetic_data import generate_synthetic_transactions
        return generate_synthetic_transactions(15)
