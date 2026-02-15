"""
Battery Smart Knowledge Base
Contains company information, policies, schemes, and FAQs.
Uses keyword matching for fast lookup (~1ms).
RESTRUCTURED: Separate _en and _hi fields for language segregation.
"""
import logging
import re

logger = logging.getLogger(__name__)

# ============================================================================
# KNOWLEDGE BASE - Structured Company Data (Language Segregated)
# ============================================================================

KNOWLEDGE_BASE = {
    # --- Company Information ---
    "company_info": {
        "mission_en": "Battery Smart aims to make electric mobility accessible and affordable for all by addressing the high upfront costs of batteries and the lack of charging infrastructure through a 'Battery-as-a-Service' (BaaS) model.",
        "mission_hi": "Battery Smart ka uddeshya electric mobility ko sabke liye sulabh aur sasti banana hai. Yeh battery ki mehengi keemat aur charging infrastructure ki kami ko 'Battery-as-a-Service' (BaaS) model ke zariye hal karta hai.",
        
        "founders_en": "Battery Smart was founded in 2019 by IIT Kanpur graduates Pulkit Khurana and Siddharth Sikka.",
        "founders_hi": "Battery Smart ki sthapna 2019 mein IIT Kanpur ke graduates Pulkit Khurana aur Siddharth Sikka ne ki thi.",
        
        "history_en": "Founded in 2019. Launched first swapping station in Janakpuri, New Delhi in June 2020. Achieved 100 million cumulative swaps by December 2025.",
        "history_hi": "2019 mein shuru hua. Pehla swapping station June 2020 mein Janakpuri, New Delhi mein launch hua. December 2025 tak 100 million swaps ka milestone haasil kiya.",
        
        "network_en": "As of late 2025, Battery Smart operates over 1,600 swapping stations across more than 50 cities in India.",
        "network_hi": "2025 ke ant tak, Battery Smart 50 se zyada shehron mein 1,600 se zyada swapping stations chala raha hai.",
        
        "cities_en": "The network includes Delhi-NCR, Lucknow, Jaipur, Karnal, Panipat, Sonipat, Meerut, Kanpur, Hyderabad, Govardhan, Vrindavan, and Mathura.",
        "cities_hi": "Network mein Delhi-NCR, Lucknow, Jaipur, Karnal, Panipat, Sonipat, Meerut, Kanpur, Hyderabad, Govardhan, Vrindavan, aur Mathura shamil hain.",
        
        "vision_en": "The 'Square Kilometer' vision - establishing a swap station in every square kilometer of operational territory to ensure zero wait time and eliminate range anxiety.",
        "vision_hi": "'Square Kilometer' vision - har ek square kilometer mein ek swap station sthapit karna taaki zero wait time ho aur range anxiety khatam ho.",
        
        "investors_en": "Lead investors include Tiger Global, Blume Ventures, Orios Venture Partners, LeapFrog Investments, MUFG Bank, and Panasonic.",
        "investors_hi": "Pramukh niveshak hain Tiger Global, Blume Ventures, Orios Venture Partners, LeapFrog Investments, MUFG Bank, aur Panasonic.",
        
        "funding_en": "As of mid-2025, Battery Smart has raised approximately $192 million in total funding, including a $65 million Series B and $29 million Series B1.",
        "funding_hi": "2025 ke madhya tak, Battery Smart ne lagbhag $192 million ki funding haasil ki hai, jisme $65 million Series B aur $29 million Series B1 shamil hai.",
        
        "revenue_en": "The company reported total revenue of Rs 279 crore in FY25, including Rs 249 crore from operations - a 52% year-on-year increase.",
        "revenue_hi": "Company ne FY25 mein Rs 279 crore ka kul revenue report kiya, jisme Rs 249 crore operations se aaya - yeh saal-dar-saal 52% ki badhottari hai.",
        
        "profitability_en": "While the company posted an EBITDA loss of Rs 56 crore in FY25, it achieved operating break-even and turned EBITDA positive toward the end of that period.",
        "profitability_hi": "FY25 mein company ne Rs 56 crore ka EBITDA loss pesh kiya, lekin isne operating break-even haasil kiya aur us samay ke ant tak EBITDA positive ho gaya.",
        
        "environmental_impact_en": "The network has enabled over 3.5 billion clean kilometers, helping avoid approximately 237,000 tonnes of CO2 emissions.",
        "environmental_impact_hi": "Network ne 3.5 billion se zyada swachh kilometers ko sambhav banaya hai, jisse lagbhag 237,000 tonne CO2 emissions se bacha gaya.",
        
        "expansion_en": "Battery Smart has a roadmap to expand into 100 additional cities by 2026, focusing on commercial corridors in UP, Rajasthan, and Haryana.",
        "expansion_hi": "Battery Smart ke paas 2026 tak 100 naye shehron mein failne ka roadmap hai, jo UP, Rajasthan, aur Haryana ke commercial corridors par kendrit hai."
    },
    
    # --- Driver Schemes & Benefits ---
    "driver_schemes": {
        "revenue_schemes_en": """Battery Smart offers multiple revenue-boosting schemes for drivers:
1. E-rickshaw drivers can increase daily earnings by 50-75%, from Rs 700-800 with lead-acid to Rs 1200-1300 with Li-ion.
2. Driver Welfare Fund 2026: Rs 10 crore initiative providing insurance, financial protection, free swaps, and skill development for 1 lakh drivers.
3. Referral and Reward Program: Earn cash incentives or free swap coupons by referring new drivers.
4. Top-performing drivers get free battery swaps.""",
        
        "revenue_schemes_hi": """Battery Smart drivers ke liye kayi revenue badhane wali schemes pesh karta hai:
1. E-rickshaw drivers apni daily kamai 50-75% badha sakte hain, lead-acid se Rs 700-800 se Li-ion se Rs 1200-1300 tak.
2. Driver Welfare Fund 2026: Rs 10 crore ki pehel jo 1 lakh drivers ko insurance, financial protection, muft swaps, aur skill development deti hai.
3. Referral aur Reward Program: Naye drivers ko refer karke cash incentives ya muft swap coupons kamayein.
4. Top-performing drivers ko muft battery swaps milte hain.""",
        
        "welfare_fund_en": "The Rs 10 crore Driver Welfare Fund 2026 provides insurance coverage, financial protection, free swaps for top performers, skill development, and referral rewards for approximately 1 lakh EV drivers.",
        "welfare_fund_hi": "Rs 10 crore ka Driver Welfare Fund 2026 lagbhag 1 lakh EV drivers ko insurance coverage, financial protection, top performers ke liye muft swaps, skill development, aur referral rewards pradaan karta hai.",
        
        "insurance_en": "Through partnership with Bharatsure, Battery Smart protects over 40,000 drivers with coverage for emergency medical treatment, hospitalization, day-care treatments, and accidental insurance including fatality or permanent disability benefits.",
        "insurance_hi": "Bharatsure ke saath partnership ke zariye, Battery Smart 40,000 se zyada drivers ko emergency medical treatment, hospitalization, day-care treatments, aur accidental insurance jisme fatality ya permanent disability benefits shamil hain, se surakshit karta hai.",
        
        "women_drivers_en": "Battery Smart supports more than 5,000 women drivers with targeted onboarding support, safety training via the Safety Hub, and community initiatives.",
        "women_drivers_hi": "Battery Smart 5,000 se zyada mahila drivers ko targeted onboarding support, Safety Hub ke zariye safety training, aur community initiatives ke saath samarthan karta hai.",
        
        "earnings_increase_en": "Drivers can increase daily earnings by 50-75%, rising from Rs 700-800 with lead-acid batteries to Rs 1200-1300 with swappable Li-ion batteries.",
        "earnings_increase_hi": "Drivers apni daily kamai 50-75% badha sakte hain, lead-acid batteries se Rs 700-800 se swappable Li-ion batteries se Rs 1200-1300 tak.",
        
        "referral_program_en": "Active drivers earn rewards by referring new operators - cash incentives credited to digital wallet or free swap coupons.",
        "referral_program_hi": "Active drivers naye operators ko refer karke rewards kamate hain - cash incentives digital wallet mein credit hote hain ya muft swap coupons milte hain."
    },
    
    # --- Partner Information ---
    "partner_info": {
        "investment_tiers_en": """Partnership tiers based on batteries managed:
- Bronze: 10-20 batteries, investment Rs 1,50,000-3,00,000, monthly profit Rs 15,000-35,000
- Silver: 30-40 batteries, investment Rs 4,50,000-6,00,000, monthly profit Rs 60,000-85,000  
- Gold: 50-60 batteries, investment Rs 7,50,000-9,00,000, monthly profit Rs 1,10,000-1,40,000""",
        
        "investment_tiers_hi": """Partnership tiers batteries ke hisaab se:
- Bronze: 10-20 batteries, nivesh Rs 1,50,000-3,00,000, mahine ka munafa Rs 15,000-35,000
- Silver: 30-40 batteries, nivesh Rs 4,50,000-6,00,000, mahine ka munafa Rs 60,000-85,000
- Gold: 50-60 batteries, nivesh Rs 7,50,000-9,00,000, mahine ka munafa Rs 1,10,000-1,40,000""",
        
        "security_deposit_en": "Security deposits range from Rs 50,000 for smallest Bronze setup to Rs 3,00,000 for largest Gold setup.",
        "security_deposit_hi": "Security deposit Rs 50,000 se sabse chhote Bronze setup ke liye Rs 3,00,000 tak sabse bade Gold setup ke liye hota hai.",
        
        "onboarding_time_en": "New station goes live in 6 weeks: Week 1 interest expression, Week 2 quality checks, Week 3 location transformation, Week 4 setup installation, Week 5 asset deployment, Week 6 going live.",
        "onboarding_time_hi": "Naya station 6 hafton mein live hota hai: Hafta 1 interest expression, Hafta 2 quality checks, Hafta 3 location transformation, Hafta 4 setup installation, Hafta 5 asset deployment, Hafta 6 going live.",
        
        "partner_support_en": "Partners receive complete infrastructure setup (chargers, batteries, racks), dedicated Partner App, 24x7 support, and demand generation through 250+ managers who help onboard drivers.",
        "partner_support_hi": "Partners ko complete infrastructure setup (chargers, batteries, racks), dedicated Partner App, 24x7 support, aur 250+ managers ke zariye demand generation milti hai jo drivers ko onboard karne mein madad karte hain."
    },
    
    # --- Swapping Process ---
    "swapping": {
        "process_en": """Battery swap takes under 2 minutes:
1. Locate nearest station via Driver App
2. Scan QR code at station to authenticate
3. Open designated slot and deposit depleted battery
4. Retrieve fully charged battery and close slot""",
        
        "process_hi": """Battery swap mein 2 minute se kam lagta hai:
1. Driver App se nearest station dhundhein
2. Station par QR code scan karein authenticate karne ke liye
3. Designated slot kholein aur khatam battery rakhein
4. Puri charge battery lein aur slot band karein""",
        
        "cost_en": "A single swap costs between Rs 100 and Rs 150.",
        "cost_hi": "Ek swap ka daam Rs 100 se Rs 150 ke beech hota hai.",
        
        "range_en": "A set of swappable batteries provides 65-75 km effective range.",
        "range_hi": "Swappable batteries ka ek set 65-75 km ki effective range deta hai.",
        
        "when_to_swap_en": "Vehicles have smart meters showing State of Charge (SoC). The Driver App sends notifications when battery is low and guides to nearest swap station.",
        "when_to_swap_hi": "Vehicles mein smart meters hote hain jo State of Charge (SoC) dikhate hain. Driver App battery low hone par notification bhejti hai aur nearest swap station tak guide karti hai."
    },
    
    # --- Battery Technical Info ---
    "battery_tech": {
        "specifications_en": "Li-ion packs weighing 12-15 kg with capacity of 2-2.5 kWh. Compared to 120 kg lead-acid batteries that can leak acid and corrode chassis.",
        "specifications_hi": "Li-ion packs ka vajan 12-15 kg hota hai jisme 2-2.5 kWh ki capacity hoti hai. 120 kg wali lead-acid batteries ki tulna mein jo acid leak kar sakti hain aur chassis ko kharab kar sakti hain.",
        
        "safety_en": "IoT-enabled BMS monitors voltage, current, temperature, and SoC in real-time. Includes fire detection and auto power disconnect for abnormal temperature or smoke.",
        "safety_hi": "IoT-enabled BMS voltage, current, temperature, aur SoC ko real-time mein monitor karta hai. Isme fire detection aur abnormal temperature ya smoke ke liye auto power disconnect shamil hai.",
        
        "chemistry_en": "Uses Lithium Iron Phosphate (LFP) or Nickel Manganese Cobalt (NMC). LFP offers high safety and 3,000+ cycle life. NMC offers higher energy density.",
        "chemistry_hi": "Lithium Iron Phosphate (LFP) ya Nickel Manganese Cobalt (NMC) use hota hai. LFP zyada suraksha aur 3,000+ cycle life deta hai. NMC zyada energy density deta hai.",
        
        "maintenance_en": "Battery Smart takes full responsibility for technical maintenance, repairs, and end-of-life recycling - no maintenance liability for drivers.",
        "maintenance_hi": "Battery Smart technical maintenance, repairs, aur end-of-life recycling ki puri zimmedari leta hai - drivers par koi maintenance liability nahi hoti."
    },
    
    # --- Policies & Rules ---
    "policies": {
        "home_charging_en": "Charging batteries at home is STRICTLY PROHIBITED. Batteries must only be charged at authorized Designated Stations. Unauthorized charging leads to penalties, BMS damage, and contract termination.",
        "home_charging_hi": "Ghar par battery charge karna SAKHT MANA HAI. Batteries sirf authorized Designated Stations par hi charge honi chahiye. Bina ijazat charging karne par penalty, BMS damage, aur contract termination hota hai.",
        
        "battery_retention_en": "Drivers cannot keep a battery for more than 5 consecutive days without visiting a station. For long leave, battery must be returned to avoid penalties or contract termination.",
        "battery_retention_hi": "Drivers 5 din se zyada lagatar battery nahi rakh sakte bina station jaaye. Lambi chutti ke liye battery wapas karni hogi warna penalty ya contract termination hoga.",
        
        "theft_damage_en": "Drivers are liable for compensation if battery is lost or damaged beyond repair. Minimum payable equals battery pack cost. Driver Welfare Fund 2026 provides some protection for such cases.",
        "theft_damage_hi": "Agar battery kho jaye ya marammat se pare kharab ho jaye to drivers ko muavza dena hoga. Kam se kam battery pack ki keemat deni hogi. Driver Welfare Fund 2026 aise cases mein kuch suraksha deta hai.",
        
        "troubleshooting_en": "For battery issues: verify credentials, check for loose connections, ensure battery isn't paired with another device, and verify app is updated to latest version.",
        "troubleshooting_hi": "Battery ki samasya ke liye: credentials verify karein, loose connections check karein, ensure karein ki battery kisi aur device ke saath paired nahi hai, aur app ko latest version mein update karein."
    },
    
    # --- Support & Help ---
    "support": {
        "helpline_en": "24x7 support helpline: +91 8055 300 400",
        "helpline_hi": "24x7 support helpline: +91 8055 300 400",
        
        "accident_reporting_en": "Use 'Real-time Help' or 'In-app reporting' features in Driver App. 24x7 helpline guides through documentation for Bharatsure claims.",
        "accident_reporting_hi": "Driver App mein 'Real-time Help' ya 'In-app reporting' features use karein. 24x7 helpline Bharatsure claims ke liye documentation mein guide karti hai.",
        
        "stuck_battery_en": "Use 'Voice Support' feature in Driver App to send voice note with location and issue. Use 'Find Your Nearest Station' tool for directions to closest swap point.",
        "stuck_battery_hi": "Driver App mein 'Voice Support' feature use karein apni location aur issue ke saath voice note bhejne ke liye. 'Find Your Nearest Station' tool use karein sabse nazdeeki swap point ke directions ke liye.",
        
        "driver_khata_en": "Digital ledger in app maintains real-time record of all daily transactions, swap fees paid, and total earnings.",
        "driver_khata_hi": "App mein digital ledger sabhi daily transactions, swap fees, aur total earnings ka real-time record rakhta hai."
    }
}

# ============================================================================
# KEYWORD MAPPINGS - For fast intent matching (maps to base key, not _en/_hi)
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
    "referral|refer|recommend": ("driver_schemes", "referral_program"),
    
    # Partner info
    "partner|franchise|invest|nivesh": ("partner_info", "investment_tiers"),
    "deposit|security|jama": ("partner_info", "security_deposit"),
    "how long|kitna time|onboard": ("partner_info", "onboarding_time"),
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
    Language-aware: returns content in user's detected language.
    """
    
    def __init__(self):
        self.kb = KNOWLEDGE_BASE
        self.mappings = KEYWORD_MAPPINGS
    
    def search(self, query: str, language: str = "english") -> dict:
        """
        Search the knowledge base for relevant information.
        
        Args:
            query: User's question or search query
            language: User's detected language ('english' or 'hindi')
        
        Returns:
            dict with:
                - found: bool
                - answer: str (the information in user's language)
                - category: str (which section it came from)
                - speech: str (TTS-friendly response)
        """
        query_lower = query.lower()
        logger.info(f"🔍 Searching KB for: {query} (language: {language})")
        
        # Determine language suffix
        lang_suffix = "_en" if language == "english" else "_hi"
        
        # Try keyword matching
        for pattern, (category, base_key) in self.mappings.items():
            if re.search(pattern, query_lower):
                # Get the language-specific key
                lang_key = base_key + lang_suffix
                
                # Check if language-specific key exists, fallback to other language
                if lang_key in self.kb[category]:
                    answer = self.kb[category][lang_key]
                else:
                    # Fallback to other language if specific one doesn't exist
                    fallback_key = base_key + ("_hi" if language == "english" else "_en")
                    answer = self.kb[category].get(fallback_key, "Information not available.")
                
                logger.info(f"✅ Found in {category}.{lang_key}")
                
                return {
                    "found": True,
                    "answer": answer,
                    "category": category,
                    "key": base_key,
                    "language": language,
                    "speech": self._generate_speech(answer)
                }
        
        # No match found - return message in user's language
        if language == "english":
            no_match_msg = "Sorry, I don't have information about that right now. Can I help you with something else?"
        else:
            no_match_msg = "Maaf kijiye, is sawaal ka jawaab mere paas abhi nahi hai. Kya main aapko kisi aur cheez mein madad kar sakti hoon?"
        
        logger.info("❌ No match in knowledge base")
        return {
            "found": False,
            "answer": None,
            "category": None,
            "language": language,
            "speech": no_match_msg
        }
    
    def _generate_speech(self, answer: str) -> str:
        """Generate TTS-friendly speech from answer."""
        # Clean up for TTS
        speech = answer.replace("₹", "rupees ")
        speech = speech.replace("Rs ", "rupees ")
        speech = speech.replace("%", " percent")
        speech = speech.replace("CO2", "carbon dioxide")
        speech = speech.replace("BMS", "battery management system")
        speech = speech.replace("IoT", "I O T")
        speech = speech.replace("SoC", "state of charge")
        speech = speech.replace("LFP", "L F P")
        speech = speech.replace("NMC", "N M C")
        
        # Limit length for voice response
        if len(speech) > 500:
            speech = speech[:500]
            last_period = speech.rfind(".")
            if last_period > 200:
                speech = speech[:last_period + 1]
        
        return speech
    
    def get_schemes(self, language: str = "english") -> dict:
        """Get driver revenue schemes specifically (for sales pitch)."""
        lang_suffix = "_en" if language == "english" else "_hi"
        key = "revenue_schemes" + lang_suffix
        answer = self.kb["driver_schemes"][key]
        return {
            "found": True,
            "answer": answer,
            "language": language,
            "speech": self._generate_speech(answer)
        }


# Singleton instance
knowledge_tool = KnowledgeBaseTool()
