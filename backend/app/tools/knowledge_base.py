"""
Battery Smart Knowledge Base
Contains company information, policies, schemes, and FAQs.
Uses keyword matching for fast lookup (~1ms).
"""
import logging
import re

logger = logging.getLogger(__name__)

# ============================================================================
# KNOWLEDGE BASE - Structured Company Data
# ============================================================================

KNOWLEDGE_BASE = {
    # --- Company Information ---
    "company_info": {
        "mission": "Battery Smart aims to make electric mobility accessible and affordable for all by addressing the high upfront costs of batteries and the lack of charging infrastructure through a 'Battery-as-a-Service' (BaaS) model.",
        "founders": "Battery Smart was founded in 2019 by IIT Kanpur graduates Pulkit Khurana and Siddharth Sikka.",
        "history": "Founded in 2019. Launched first swapping station in Janakpuri, New Delhi in June 2020. Achieved 100 million cumulative swaps by December 2025.",
        "network": "As of late 2025, Battery Smart operates over 1,600 swapping stations across more than 50 cities in India.",
        "cities": "The network includes Delhi-NCR, Lucknow, Jaipur, Karnal, Panipat, Sonipat, Meerut, Kanpur, Hyderabad, Govardhan, Vrindavan, and Mathura.",
        "vision": "The 'Square Kilometer' vision - establishing a swap station in every square kilometer of operational territory to ensure zero wait time and eliminate range anxiety.",
        "investors": "Lead investors include Tiger Global, Blume Ventures, Orios Venture Partners, LeapFrog Investments, MUFG Bank, and Panasonic.",
        "funding": "As of mid-2025, Battery Smart has raised approximately $192 million in total funding, including a $65 million Series B and $29 million Series B1.",
        "revenue": "The company reported total revenue of ₹279 crore in FY25, including ₹249 crore from operations—a 52% year-on-year increase.",
        "profitability": "While the company posted an EBITDA loss of ₹56 crore in FY25, it achieved operating break-even and turned EBITDA positive toward the end of that period.",
        "environmental_impact": "The network has enabled over 3.5 billion clean kilometers, helping avoid approximately 237,000 tonnes of CO2 emissions.",
        "expansion": "Battery Smart has a roadmap to expand into 100 additional cities by 2026, focusing on commercial corridors in UP, Rajasthan, and Haryana."
    },
    
    # --- Driver Schemes & Benefits ---
    "driver_schemes": {
        "revenue_schemes": """Battery Smart offers multiple revenue-boosting schemes for drivers:
1. E-rickshaw drivers can increase daily earnings by 50-75%, from ₹700-₹800 with lead-acid to ₹1200-₹1300 with Li-ion.
2. Driver Welfare Fund 2026: ₹10 crore initiative providing insurance, financial protection, free swaps, and skill development for 1 lakh drivers.
3. Referral and Reward Program: Earn cash incentives or free swap coupons by referring new drivers.
4. Top-performing drivers get free battery swaps.""",
        
        "welfare_fund": "The ₹10 crore Driver Welfare Fund 2026 provides insurance coverage, financial protection, free swaps for top performers, skill development, and referral rewards for approximately 1 lakh EV drivers.",
        
        "insurance": "Through partnership with Bharatsure, Battery Smart protects over 40,000 drivers with coverage for emergency medical treatment, hospitalization, day-care treatments, and accidental insurance including fatality or permanent disability benefits.",
        
        "women_drivers": "Battery Smart supports more than 5,000 women drivers with targeted onboarding support, safety training via the Safety Hub, and community initiatives.",
        
        "earnings_increase": "Drivers can increase daily earnings by 50-75%, rising from ₹700-₹800 with lead-acid batteries to ₹1200-₹1300 with swappable Li-ion batteries.",
        
        "referral_program": "Active drivers earn rewards by referring new operators - cash incentives credited to digital wallet or free swap coupons."
    },
    
    # --- Partner Information ---
    "partner_info": {
        "investment_tiers": """Partnership tiers based on batteries managed:
- Bronze: 10-20 batteries, investment ₹1,50,000-₹3,00,000, monthly profit ₹15,000-₹35,000
- Silver: 30-40 batteries, investment ₹4,50,000-₹6,00,000, monthly profit ₹60,000-₹85,000  
- Gold: 50-60 batteries, investment ₹7,50,000-₹9,00,000, monthly profit ₹1,10,000-₹1,40,000""",
        
        "security_deposit": "Security deposits range from ₹50,000 for smallest Bronze setup to ₹3,00,000 for largest Gold setup.",
        
        "onboarding_time": "New station goes live in 6 weeks: Week 1 interest expression, Week 2 quality checks, Week 3 location transformation, Week 4 setup installation, Week 5 asset deployment, Week 6 going live.",
        
        "partner_support": "Partners receive complete infrastructure setup (chargers, batteries, racks), dedicated Partner App, 24x7 support, and demand generation through 250+ managers who help onboard drivers."
    },
    
    # --- Swapping Process ---
    "swapping": {
        "process": """Battery swap takes under 2 minutes:
1. Locate nearest station via Driver App
2. Scan QR code at station to authenticate
3. Open designated slot and deposit depleted battery
4. Retrieve fully charged battery and close slot""",
        
        "cost": "A single swap costs between ₹100 and ₹150.",
        
        "range": "A set of swappable batteries provides 65-75 km effective range.",
        
        "when_to_swap": "Vehicles have smart meters showing State of Charge (SoC). The Driver App sends notifications when battery is low and guides to nearest swap station."
    },
    
    # --- Battery Technical Info ---
    "battery_tech": {
        "specifications": "Li-ion packs weighing 12-15 kg with capacity of 2-2.5 kWh. Compared to 120 kg lead-acid batteries that can leak acid and corrode chassis.",
        
        "safety": "IoT-enabled BMS monitors voltage, current, temperature, and SoC in real-time. Includes fire detection and auto power disconnect for abnormal temperature or smoke.",
        
        "chemistry": "Uses Lithium Iron Phosphate (LFP) or Nickel Manganese Cobalt (NMC). LFP offers high safety and 3,000+ cycle life. NMC offers higher energy density.",
        
        "maintenance": "Battery Smart takes full responsibility for technical maintenance, repairs, and end-of-life recycling—no maintenance liability for drivers."
    },
    
    # --- Policies & Rules ---
    "policies": {
        "home_charging": "Charging batteries at home is STRICTLY PROHIBITED. Batteries must only be charged at authorized Designated Stations. Unauthorized charging leads to penalties, BMS damage, and contract termination.",
        
        "battery_retention": "Drivers cannot keep a battery for more than 5 consecutive days without visiting a station. For long leave, battery must be returned to avoid penalties or contract termination.",
        
        "theft_damage": "Drivers are liable for compensation if battery is lost or damaged beyond repair. Minimum payable equals battery pack cost. Driver Welfare Fund 2026 provides some protection for such cases.",
        
        "troubleshooting": "For battery issues: verify credentials, check for loose connections, ensure battery isn't paired with another device, and verify app is updated to latest version."
    },
    
    # --- Support & Help ---
    "support": {
        "helpline": "24x7 support helpline: +91 8055 300 400",
        
        "accident_reporting": "Use 'Real-time Help' or 'In-app reporting' features in Driver App. 24x7 helpline guides through documentation for Bharatsure claims.",
        
        "stuck_battery": "Use 'Voice Support' feature in Driver App to send voice note with location and issue. Use 'Find Your Nearest Station' tool for directions to closest swap point.",
        
        "driver_khata": "Digital ledger in app maintains real-time record of all daily transactions, swap fees paid, and total earnings."
    }
}

# ============================================================================
# KEYWORD MAPPINGS - For fast intent matching
# ============================================================================

KEYWORD_MAPPINGS = {
    # Company queries
    "mission|goal|aim|uddeshya": ("company_info", "mission"),
    "founder|who started|kisne banaya|owner|malik": ("company_info", "founders"),
    "history|when started|kab shuru": ("company_info", "history"),
    "cities|sheher|kahan kahan|locations": ("company_info", "cities"),
    "stations|kitne station|network": ("company_info", "network"),
    "vision|future|bhavishya": ("company_info", "vision"),
    "investor|funding|paisa kahan se": ("company_info", "investors"),
    "revenue|kamai|income": ("company_info", "revenue"),
    "profit|faayda|munafa": ("company_info", "profitability"),
    "environment|pollution|green|co2": ("company_info", "environmental_impact"),
    "expansion|new cities|naye sheher": ("company_info", "expansion"),
    
    # Driver schemes
    "scheme|yojana|offer|revenue scheme|earning scheme": ("driver_schemes", "revenue_schemes"),
    "welfare fund|driver fund|10 crore": ("driver_schemes", "welfare_fund"),
    "insurance|bima|protection": ("driver_schemes", "insurance"),
    "women|mahila|lady driver": ("driver_schemes", "women_drivers"),
    "earnings|kamai|kitna milega|income increase": ("driver_schemes", "earnings_increase"),
    "referral|refer karke|invite": ("driver_schemes", "referral_program"),
    
    # Partner info
    "partner|franchise|investment|nivesh": ("partner_info", "investment_tiers"),
    "deposit|security|jama": ("partner_info", "security_deposit"),
    "onboarding|new station|station kholna": ("partner_info", "onboarding_time"),
    "partner support|partner help": ("partner_info", "partner_support"),
    
    # Swapping
    "swap process|kaise karte|how to swap": ("swapping", "process"),
    "swap cost|kitna paisa|price|rate": ("swapping", "cost"),
    "range|kitna chalega|distance": ("swapping", "range"),
    "when swap|kab swap|low battery": ("swapping", "when_to_swap"),
    
    # Battery tech
    "battery specification|weight|capacity": ("battery_tech", "specifications"),
    "safety|suraksha|safe hai": ("battery_tech", "safety"),
    "chemistry|lfp|nmc|technology": ("battery_tech", "chemistry"),
    "maintenance|repair|service": ("battery_tech", "maintenance"),
    
    # Policies
    "home charging|ghar pe charge|charge at home": ("policies", "home_charging"),
    "keep battery|kitne din|retention": ("policies", "battery_retention"),
    "theft|chori|damage|lost battery": ("policies", "theft_damage"),
    "troubleshoot|problem|issue|kaam nahi": ("policies", "troubleshooting"),
    
    # Support
    "helpline|phone|call|contact": ("support", "helpline"),
    "accident|insurance claim|report": ("support", "accident_reporting"),
    "stuck|emergency|battery dead": ("support", "stuck_battery"),
    "khata|ledger|transaction|history": ("support", "driver_khata")
}


class KnowledgeBaseTool:
    """
    Tool to search the Battery Smart knowledge base.
    Uses keyword matching for fast (~1ms) lookups.
    """
    
    def __init__(self):
        self.kb = KNOWLEDGE_BASE
        self.mappings = KEYWORD_MAPPINGS
    
    def search(self, query: str) -> dict:
        """
        Search the knowledge base for relevant information.
        
        Args:
            query: User's question or search query
        
        Returns:
            dict with:
                - found: bool
                - answer: str (the information)
                - category: str (which section it came from)
                - speech: str (TTS-friendly response)
        """
        query_lower = query.lower()
        logger.info(f"🔍 Searching KB for: {query}")
        
        # Try keyword matching
        for pattern, (category, key) in self.mappings.items():
            if re.search(pattern, query_lower):
                answer = self.kb[category][key]
                logger.info(f"✅ Found in {category}.{key}")
                
                return {
                    "found": True,
                    "answer": answer,
                    "category": category,
                    "key": key,
                    "speech": self._generate_speech(answer)
                }
        
        # No match found
        logger.info("❌ No match in knowledge base")
        return {
            "found": False,
            "answer": None,
            "category": None,
            "speech": "Maaf kijiye, is sawaal ka jawaab mere paas abhi nahi hai. Kya main aapko kisi aur cheez mein madad kar sakti hoon?"
        }
    
    def _generate_speech(self, answer: str) -> str:
        """Generate TTS-friendly speech from answer."""
        # Clean up for TTS
        speech = answer.replace("₹", "rupees ")
        speech = speech.replace("%", " percent")
        speech = speech.replace("CO2", "carbon dioxide")
        speech = speech.replace("BMS", "battery management system")
        speech = speech.replace("IoT", "I O T")
        speech = speech.replace("SoC", "state of charge")
        speech = speech.replace("LFP", "L F P")
        speech = speech.replace("NMC", "N M C")
        
        # Limit length for voice response
        if len(speech) > 500:
            # Take first 500 chars and end at sentence
            speech = speech[:500]
            last_period = speech.rfind(".")
            if last_period > 200:
                speech = speech[:last_period + 1]
        
        return speech
    
    def get_schemes(self) -> dict:
        """Get driver revenue schemes specifically (for sales pitch)."""
        return {
            "found": True,
            "answer": self.kb["driver_schemes"]["revenue_schemes"],
            "speech": self._generate_speech(self.kb["driver_schemes"]["revenue_schemes"])
        }


# Singleton instance
knowledge_tool = KnowledgeBaseTool()
