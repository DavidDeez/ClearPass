"""
Module 8 — Squad Financial Enforcement Layer (Layer 4)
======================================================
Integrates with the Squad API for virtual accounts, transfers, and
payout auditing. Implements the "Causal Gate" rule: payouts are
only executed if the ClearPass Trust Score is above a safety threshold.
"""

import logging
import os
from typing import Any, Dict
import httpx

logger = logging.getLogger("clearpass.squad")

SQUAD_SECRET_KEY = os.environ.get("SQUAD_SECRET_KEY", "sk_test_mock_key")
SQUAD_BASE_URL = "https://sandbox-api.squadco.com" # Switch to production for live
TRUST_SCORE_THRESHOLD = 60

class SquadService:
    @staticmethod
    async def create_virtual_account(bvn: str, first_name: str, last_name: str) -> Dict[str, Any]:
        """
        Create a dynamic virtual account for the user to facilitate
        SaaS billing or loan repayments.
        """
        logger.info("Squad: Creating virtual account for BVN %s", bvn[:6] + "****")
        
        # In a real app, this would be an API call to Squad
        # return {"account_number": "0123456789", "bank_name": "Squad Bank"}
        
        # Mocking for demo
        return {
            "virtual_account_number": f"99{bvn[:8]}",
            "bank_name": "GTBank (via Squad)",
            "beneficiary_name": f"{first_name} {last_name}",
            "currency": "NGN"
        }

    @staticmethod
    async def execute_conditional_payout(bvn: str, amount: float, trust_score: int, destination_account: str):
        """
        The Causal Gate: Execute a transfer only if the trust score is safe.
        """
        logger.info("Squad: Payout request for BVN %s | Score: %d | Amount: ₦%.2f", 
                    bvn[:6], trust_score, amount)
        
        if trust_score < TRUST_SCORE_THRESHOLD:
            logger.warning("Squad: Payout BLOCKED by Causal Gate (Score %d < %d)", 
                           trust_score, TRUST_SCORE_THRESHOLD)
            return {
                "status": "blocked",
                "reason": "insufficient_trust_score",
                "threshold": TRUST_SCORE_THRESHOLD
            }
        
        # Execute Squad Transfer API call
        # Mocking success
        logger.info("Squad: Payout EXECUTED successfully to %s", destination_account)
        return {
            "status": "success",
            "transaction_reference": f"SQ-TX-{os.urandom(4).hex().upper()}",
            "amount": amount,
            "recipient": destination_account
        }

    @staticmethod
    def audit_verification(bvn: str, cost_naira: float = 200.0):
        """
        Log the billing for a verification (SaaS Model: ₦200 per verify).
        """
        logger.info("Squad: Billing audit — ₦%.2f charged for BVN %s", cost_naira, bvn[:6])
        return {"billed": True, "amount": cost_naira}
