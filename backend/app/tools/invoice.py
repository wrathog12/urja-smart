"""
Invoice Tool - Multi-phase driver invoice lookup
Handles: Driver ID collection → Confirmation → Invoice Summary/Details

Phases:
- idle: No invoice query in progress
- awaiting_id: Asked user for driver ID
- confirming: Confirming the driver ID with user
- confirmed: ID confirmed, can provide details
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ============================================================================
# STATIC INVOICE DATA (simulating database)
# ============================================================================
INVOICES = {
    "DRM": {
        "driver_id": "DRM",
        "swaps_summary": {
            "total_swaps_month": 35,
            "primary_swaps": {"count": 20, "rate": 170, "cost": 3400},
            "secondary_swaps": {"count": 15, "rate": 70, "cost": 1050}
        },
        "penalty_summary": {
            "total_incidents": 6,
            "exempted_incidents": 4,
            "chargeable_incidents": 2,
            "penalty_rate": 120,
            "total_penalty_cost": 240,
            "penalty_diverted": 120
        },
        "financials": {
            "total_swap_cost": 4450,
            "net_penalty_payable": 120,
            "final_total_payable": 4570
        }
    },
    "DRC": {
        "driver_id": "DRC",
        "swaps_summary": {
            "total_swaps_month": 45,
            "primary_swaps": {"count": 25, "rate": 170, "cost": 4250},
            "secondary_swaps": {"count": 20, "rate": 70, "cost": 1400}
        },
        "penalty_summary": {
            "total_incidents": 3,
            "exempted_incidents": 4,
            "chargeable_incidents": 0,
            "penalty_rate": 120,
            "total_penalty_cost": 0,
            "penalty_diverted": 0
        },
        "financials": {
            "total_swap_cost": 5650,
            "net_penalty_payable": 0,
            "final_total_payable": 5650
        }
    },
    "DRB": {
        "driver_id": "DRB",
        "swaps_summary": {
            "total_swaps_month": 22,
            "primary_swaps": {"count": 15, "rate": 170, "cost": 2550},
            "secondary_swaps": {"count": 7, "rate": 70, "cost": 490}
        },
        "penalty_summary": {
            "total_incidents": 10,
            "exempted_incidents": 4,
            "chargeable_incidents": 6,
            "penalty_rate": 120,
            "total_penalty_cost": 720,
            "penalty_diverted": 300
        },
        "financials": {
            "total_swap_cost": 3040,
            "net_penalty_payable": 420,
            "final_total_payable": 3460
        }
    },
    "DRD": {
        "driver_id": "DRD",
        "swaps_summary": {
            "total_swaps_month": 18,
            "primary_swaps": {"count": 18, "rate": 170, "cost": 3060},
            "secondary_swaps": {"count": 0, "rate": 70, "cost": 0}
        },
        "penalty_summary": {
            "total_incidents": 5,
            "exempted_incidents": 4,
            "chargeable_incidents": 1,
            "penalty_rate": 120,
            "total_penalty_cost": 120,
            "penalty_diverted": 60
        },
        "financials": {
            "total_swap_cost": 3060,
            "net_penalty_payable": 60,
            "final_total_payable": 3120
        }
    },
    "DRF": {
        "driver_id": "DRF",
        "swaps_summary": {
            "total_swaps_month": 60,
            "primary_swaps": {"count": 28, "rate": 170, "cost": 4760},
            "secondary_swaps": {"count": 32, "rate": 70, "cost": 2240}
        },
        "penalty_summary": {
            "total_incidents": 8,
            "exempted_incidents": 4,
            "chargeable_incidents": 4,
            "penalty_rate": 120,
            "total_penalty_cost": 480,
            "penalty_diverted": 480
        },
        "financials": {
            "total_swap_cost": 7000,
            "net_penalty_payable": 0,
            "final_total_payable": 7000
        }
    }
}


class InvoiceTool:
    """
    Multi-phase invoice lookup tool with state machine.
    Handles driver ID collection, confirmation, and invoice details.
    """
    
    def __init__(self):
        self.state = "idle"  # idle, awaiting_id, confirming, confirmed
        self.pending_driver_id: Optional[str] = None
        self.confirmed_driver_id: Optional[str] = None
    
    def reset(self):
        """Reset state for new conversation."""
        self.state = "idle"
        self.pending_driver_id = None
        self.confirmed_driver_id = None
        logger.info("🧾 Invoice tool state reset")
    
    def _normalize_driver_id(self, driver_id: str) -> str:
        """
        Normalize driver ID format.
        Accepts: "D105", "d105", "105" → Returns: "D105"
        """
        driver_id = driver_id.strip().upper()
        
        # If user just said digits, add the D prefix
        if driver_id.isdigit():
            driver_id = f"D{driver_id}"
        
        # Ensure proper format (D followed by digits)
        if not driver_id.startswith("D"):
            driver_id = f"D{driver_id}"
        
        return driver_id
    
    def initiate(self) -> dict:
        """
        Phase 1: User asks for invoice, we ask for their driver ID.
        """
        self.state = "awaiting_id"
        logger.info("🧾 Invoice flow initiated - awaiting driver ID")
        
        return {
            "speech": "Ji zaroor! Aapki Driver ID kya hai?",
            "action": "ask_id",
            "state": self.state
        }
    
    def receive_id(self, driver_id: str) -> dict:
        """
        Phase 2: User provides their ID, we validate and ask for confirmation.
        """
        normalized_id = self._normalize_driver_id(driver_id)
        logger.info(f"🧾 Received driver ID: {driver_id} → normalized: {normalized_id}")
        
        # Check if driver ID exists in our data
        if normalized_id not in INVOICES:
            logger.warning(f"🧾 Driver ID not found: {normalized_id}")
            return {
                "speech": f"Maaf kijiye, {normalized_id} ID humare system mein nahi mili. Kya aap dobara sahi ID bata sakte hain?",
                "action": "id_not_found",
                "state": self.state
            }
        
        # ID found, ask for confirmation
        self.pending_driver_id = normalized_id
        self.state = "confirming"
        logger.info(f"🧾 Asking confirmation for ID: {normalized_id}")
        
        return {
            "speech": f"Aapki Driver ID {normalized_id} hai, kya yeh sahi hai?",
            "action": "confirm",
            "state": self.state,
            "driver_id": normalized_id
        }
    
    def confirm(self, confirmed: bool) -> dict:
        """
        Phase 3: User confirms or denies the driver ID.
        """
        if confirmed:
            self.confirmed_driver_id = self.pending_driver_id
            self.state = "confirmed"
            logger.info(f"🧾 Driver ID confirmed: {self.confirmed_driver_id}")
            
            # Return invoice summary
            return self.get_summary()
        else:
            # User said no, ask for correct ID
            self.pending_driver_id = None
            self.state = "awaiting_id"
            logger.info("🧾 Driver denied ID, asking again")
            
            return {
                "speech": "Theek hai, kripya apni sahi Driver ID bataiye.",
                "action": "ask_id_again",
                "state": self.state
            }
    
    def get_summary(self) -> dict:
        """
        Get basic invoice summary for the confirmed driver.
        Called after ID confirmation or directly if ID already confirmed.
        """
        if self.state != "confirmed" or not self.confirmed_driver_id:
            logger.warning("🧾 Attempted to get summary without confirmed ID")
            return self.initiate()
        
        invoice = INVOICES.get(self.confirmed_driver_id)
        if not invoice:
            return {
                "speech": "Maaf kijiye, aapka invoice data nahi mil raha. Kripya baad mein try karein.",
                "action": "error",
                "state": self.state
            }
        
        swaps = invoice["swaps_summary"]
        financials = invoice["financials"]
        
        total_swaps = swaps["total_swaps_month"]
        total_cost = financials["final_total_payable"]
        
        speech = (
            f"Main dekh rahi hoon, aapke iss month total {total_swaps} swaps hue hain "
            f"aur aapka total payable amount {total_cost} rupees hai. "
            f"Kya aapko aur koi detail chahiye jaise penalty ya swap breakdown?"
        )
        
        logger.info(f"🧾 Returning summary for {self.confirmed_driver_id}: {total_swaps} swaps, ₹{total_cost}")
        
        return {
            "speech": speech,
            "action": "summary",
            "state": self.state,
            "data": {
                "driver_id": self.confirmed_driver_id,
                "total_swaps": total_swaps,
                "total_cost": total_cost
            }
        }
    
    def get_penalty_details(self) -> dict:
        """
        Get detailed penalty breakdown for the confirmed driver.
        Called when user explicitly asks about penalties.
        """
        if self.state != "confirmed" or not self.confirmed_driver_id:
            logger.warning("🧾 Attempted to get penalty without confirmed ID")
            return self.initiate()
        
        invoice = INVOICES.get(self.confirmed_driver_id)
        if not invoice:
            return {
                "speech": "Maaf kijiye, penalty data nahi mil raha.",
                "action": "error",
                "state": self.state
            }
        
        penalty = invoice["penalty_summary"]
        
        total_incidents = penalty["total_incidents"]
        exempted = penalty["exempted_incidents"]
        chargeable = penalty["chargeable_incidents"]
        penalty_cost = penalty["total_penalty_cost"]
        diverted = penalty["penalty_diverted"]
        net_penalty = invoice["financials"]["net_penalty_payable"]
        
        if chargeable == 0:
            speech = (
                f"Aapke iss month {total_incidents} incidents hue the, "
                f"lekin {exempted} exempted the isliye aapko koi penalty nahi lagti. "
                f"Bahut accha performance hai!"
            )
        else:
            speech = (
                f"Aapke iss month {total_incidents} incidents hue, "
                f"jinme se {exempted} exempted the. "
                f"{chargeable} chargeable incidents ke liye penalty {penalty_cost} rupees bani, "
                f"lekin {diverted} rupees diverted ho gaye. "
                f"Aapko sirf {net_penalty} rupees penalty pay karni hai."
            )
        
        logger.info(f"🧾 Returning penalty details for {self.confirmed_driver_id}")
        
        return {
            "speech": speech,
            "action": "penalty_details",
            "state": self.state,
            "data": penalty
        }
    
    def get_swap_details(self) -> dict:
        """
        Get detailed swap breakdown for the confirmed driver.
        Called when user explicitly asks about swap details.
        """
        if self.state != "confirmed" or not self.confirmed_driver_id:
            logger.warning("🧾 Attempted to get swaps without confirmed ID")
            return self.initiate()
        
        invoice = INVOICES.get(self.confirmed_driver_id)
        if not invoice:
            return {
                "speech": "Maaf kijiye, swap data nahi mil raha.",
                "action": "error",
                "state": self.state
            }
        
        swaps = invoice["swaps_summary"]
        
        primary = swaps["primary_swaps"]
        secondary = swaps["secondary_swaps"]
        total = swaps["total_swaps_month"]
        total_cost = invoice["financials"]["total_swap_cost"]
        
        speech = (
            f"Aapke total {total} swaps ka breakdown yeh hai: "
            f"{primary['count']} primary swaps at {primary['rate']} rupees, "
            f"total {primary['cost']} rupees. "
        )
        
        if secondary["count"] > 0:
            speech += (
                f"Aur {secondary['count']} secondary swaps at {secondary['rate']} rupees, "
                f"total {secondary['cost']} rupees. "
            )
        
        speech += f"Grand total swap cost hai {total_cost} rupees."
        
        logger.info(f"🧾 Returning swap details for {self.confirmed_driver_id}")
        
        return {
            "speech": speech,
            "action": "swap_details",
            "state": self.state,
            "data": swaps
        }
    
    def get_full_invoice(self) -> dict:
        """
        Get complete invoice data (for UI display or API response).
        """
        if not self.confirmed_driver_id:
            return None
        return INVOICES.get(self.confirmed_driver_id)


# Singleton instance
invoice_tool = InvoiceTool()
