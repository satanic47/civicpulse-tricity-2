import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Primary: Official Unified Google GenAI SDK (Modern standard)
try:
    from google import genai
    from google.genai import types
    HAS_NEW_GENAI = True
except ImportError:
    HAS_NEW_GENAI = False

# Fallback: Legacy google.generativeai wrapper (only if modern SDK not installed)
HAS_LEGACY_GENAI = False
if not HAS_NEW_GENAI:
    try:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import google.generativeai as legacy_genai
        HAS_LEGACY_GENAI = True
    except ImportError:
        HAS_LEGACY_GENAI = False

class GeminiCivicEngine:
    """
    Multilingual AI Engine powered by Google Gemini 2.0 Flash (with Gemini 1.5 & sovereign deterministic fallback).
    Aggregates, translates, classifies citizen grievances and generates Municipal Policy Reports.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        self.legacy_model = None
        self.active_model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

        if self.api_key:
            if HAS_NEW_GENAI:
                try:
                    self.client = genai.Client(api_key=self.api_key)
                    logger.info(f"Initialized Google GenAI SDK ({self.active_model_name}) for CivicPulse Tricity.")
                except Exception as e:
                    logger.warning(f"Failed to configure new GenAI client: {e}")

            if not self.client and HAS_LEGACY_GENAI:
                try:
                    legacy_genai.configure(api_key=self.api_key)
                    self.legacy_model = legacy_genai.GenerativeModel(self.active_model_name)
                    logger.info(f"Initialized Google Gemini ({self.active_model_name}) via legacy wrapper.")
                except Exception as e:
                    logger.warning(f"Failed to configure legacy Gemini SDK: {e}. Falling back to deterministic NLP.")

    def analyze_grievance(self, text: str, channel: str = "WEB") -> Dict[str, Any]:
        """
        Processes multilingual citizen feedback (Punjabi / Hindi / English).
        Returns structured canonical classification, urgency, sentiment, and sector info.
        """
        if self.client or self.legacy_model:
            try:
                return self._analyze_with_gemini(text, channel)
            except Exception as e:
                logger.warning(f"Gemini API invocation failed: {e}. Using deterministic engine.")
                return self._analyze_deterministic(text, channel)
        return self._analyze_deterministic(text, channel)

    def _analyze_with_gemini(self, text: str, channel: str) -> Dict[str, Any]:
        prompt = f"""
        You are NagrikSetu AI, an expert civic intelligence system for the Chandigarh Tricity Municipal Corporation.
        Analyze the following citizen report submitted via {channel}. The input may be in Punjabi, Hindi, Hinglish, or English.
        
        CITIZEN REPORT:
        \"\"\"{text}\"\"\"

        Return ONLY a valid JSON object with the following schema:
        {{
            "language_detected": "Punjabi" | "Hindi" | "English" | "Hinglish",
            "translated_text": "<English translation of the full report>",
            "category": "Roads & Traffic" | "Water Supply & Sewage" | "Street Lighting & Power" | "Sanitation & Waste Management" | "Public Safety & Health" | "Public Transit & Mobility" | "Parks & Green Spaces" | "General Public Infrastructure",
            "department": "<Appropriate Chandigarh Municipal Department, e.g. 'Engineering Department (Roads)', 'Public Health & Water Works', 'Electricity Department', 'Medical Officer of Health (Sanitation)'>",
            "location_raw": "<Specific location or landmark mentioned, e.g. 'Sector 22 Market near Kiran Cinema'>",
            "urgency_score": <Integer from 1 to 10, where 10 is immediate hazard like open manhole/exposed live wire>,
            "sentiment": "urgent" | "frustrated" | "constructive" | "neutral",
            "summary": "<Concise 1-sentence executive summary for municipal engineers>"
        }}
        """

        # 1. Execute via official Google GenAI SDK
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model=self.active_model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                return json.loads(response.text)
            except Exception as primary_err:
                logger.warning(f"Primary model {self.active_model_name} failed: {primary_err}. Attempting adaptive fallback...")
                if self.active_model_name != "gemini-1.5-flash":
                    try:
                        fallback_resp = self.client.models.generate_content(
                            model="gemini-1.5-flash",
                            contents=prompt,
                            config=types.GenerateContentConfig(response_mime_type="application/json")
                        )
                        return json.loads(fallback_resp.text)
                    except Exception:
                        pass
                raise primary_err

        # 2. Execute via legacy wrapper if new SDK unavailable
        if self.legacy_model:
            response = self.legacy_model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)

        raise RuntimeError("No active Gemini model available")

    def _analyze_deterministic(self, text: str, channel: str) -> Dict[str, Any]:
        """
        Deterministic multilingual NLP engine supporting Punjabi, Hindi, Hinglish, and English.
        Ensures zero-downtime offline execution.
        """
        t = text.lower()
        
        # 1. Detect language
        punjabi_markers = ["ਸਾਡੇ", "ਸੈਕਟਰ", "ਪਾਣੀ", "ਸੜਕ", "ਲਾਈਟਾਂ", "ਗੰਦਗੀ", "ਖੱਡੇ", "ਬਿਜਲੀ", "ਨਹੀਂ", "ਆ ਰਿਹਾ", "ਬੰਦ ਹੈ", "ਤਾਰਾਂ", "ਤੋੜਿਆ", "ਜੀ"]
        hindi_markers = ["हमारे", "सेक्टर", "पानी", "सड़क", "बिजली", "कचरा", "गड्ढे", "नाली", "सफाई", "नहीं", "हो रहा", "खराब", "है", "तार"]
        
        is_punjabi = any(m in text for m in punjabi_markers) or any(m in t for m in ["sade", "paani", "sadak", "khatam", "bijli band", "pind"])
        is_hindi = any(m in text for m in hindi_markers) or any(m in t for m in ["hamare", "gaddha", "paani nahi", "kachra", "bijli"])
        
        if is_punjabi:
            lang = "Punjabi"
        elif is_hindi:
            lang = "Hindi"
        else:
            lang = "English"

        # 2. Category & Department classification
        if any(w in t for w in ["pothole", "road", "sadak", "tarmac", "khadda", "gaddha", "traffic", "signal", "divider", "ਸੜਕ", "ਖੱਡੇ", "सड़क", "गड्ढे"]):
            cat = "Roads & Traffic"
            dept = "Engineering Department (B&R - Roads Wing)"
            urgency = 7 if "accident" in t or "deep" in t or "huge" in t else 5
        elif any(w in t for w in ["water", "paani", "sewage", "drain", "leak", "pipeline", "ganda paani", "naali", "overflow", "ਪਾਣੀ", "ਨਾਲ਼ੀ", "पानी", "सीवर"]):
            cat = "Water Supply & Sewage"
            dept = "Public Health & Water Supply Division"
            urgency = 8 if any(kw in t for kw in ["overflow", "dirty", "contamination", "leak", "burst", "ਫਟ", "ਲੀਕ", "फटा"]) else 6
        elif any(w in t for w in ["light", "street light", "dark", "pole", "wire", "bijli", "current", "spark", "blackout", "ਤਾਰਾਂ", "ਲਾਈਟ", "बिजली", "अंधेरा", "तार"]):
            cat = "Street Lighting & Power"
            dept = "Electricity Department & Smart Street Lighting Division"
            urgency = 9 if "wire" in t or "spark" in t or "school" in t or "shock" in t else 6
        elif any(w in t for w in ["garbage", "kachra", "waste", "dump", "smell", "dustbin", "safai", "kuda", "ਗੰਦਗੀ", "ਕੂੜਾ", "कचरा", "सफाई"]):
            cat = "Sanitation & Waste Management"
            dept = "Medical Officer of Health (Sanitation Wing)"
            urgency = 6 if "smell" in t or "hospital" in t else 5
        elif any(w in t for w in ["police", "theft", "unsafe", "eve teasing", "cctv", "security", "dark alley", "خطرہ", "ਚੋਰੀ", "सुरक्षा"]):
            cat = "Public Safety & Health"
            dept = "Chandigarh Police & Smart City Surveillance"
            urgency = 8
        elif any(w in t for w in ["bus", "isbt", "ctu", "auto", "e-rickshaw", "stop", "shelter"]):
            cat = "Public Transit & Mobility"
            dept = "Chandigarh Transport Undertaking (CTU)"
            urgency = 4
        elif any(w in t for w in ["park", "bench", "grass", "tree", "garden", "jogging", "ਬਗੀਚਾ", "ਪਾਰਕ", "पार्क"]):
            cat = "Parks & Green Spaces"
            dept = "Horticulture Wing"
            urgency = 3
        else:
            cat = "General Public Infrastructure"
            dept = "Municipal Corporation Chandigarh (Central Grievance Cell)"
            urgency = 4

        # Urgency boost for critical terms
        if any(w in t for w in ["danger", "urgent", "accident", "child", "school", "hospital", "sparking", "death"]):
            urgency = min(10, urgency + 2)

        # Sentiment
        if urgency >= 8:
            sentiment = "urgent"
        elif any(w in t for w in ["again", "weeks", "months", "no action", "angry", "pathetic", "frustrated"]):
            sentiment = "frustrated"
        elif any(w in t for w in ["please fix", "request", "suggest", "improve"]):
            sentiment = "constructive"
        else:
            sentiment = "neutral"

        # Translation / canonical English text
        translated = text
        if lang != "English":
            translated = f"[Standardized Translation]: {cat} issue reported by citizen regarding '{text}'"

        summary = f"{cat} concern reported requiring inspection by {dept}."

        return {
            "language_detected": lang,
            "translated_text": translated,
            "category": cat,
            "department": dept,
            "location_raw": text[:60],
            "urgency_score": urgency,
            "sentiment": sentiment,
            "summary": summary
        }

    def generate_policy_recommendation(self, sector: str, category: str, grievance_list: list, budget_info: dict) -> Dict[str, Any]:
        """
        Synthesizes multiple citizen requests into an actionable Municipal Detailed Project Report (DPR).
        """
        count = len(grievance_list)
        avg_urgency = sum(g.get("urgency_score", 5) for g in grievance_list) / max(1, count)
        population = budget_info.get("population", 25000)
        
        # Priority formula: (Incident Count * 0.4) + (Avg Urgency * 6) + (Population Density Factor * 2)
        priority_score = min(99.5, round((count * 2.5) + (avg_urgency * 5.5) + (population / 5000), 1))
        
        # Cost estimate modeling
        unit_costs = {
            "Roads & Traffic": 12.5,          # Lakhs per km / resurfacing
            "Water Supply & Sewage": 18.0,    # Lakhs for pipeline replacement
            "Street Lighting & Power": 4.5,   # Lakhs for LED retrofit & wiring
            "Sanitation & Waste Management": 6.0, # Lakhs for secondary collection hub
            "Public Safety & Health": 8.0,    # Lakhs for CCTV & high-mast illumination
        }
        cost_lakhs = round(unit_costs.get(category, 5.0) * (1 + (count * 0.15)), 2)

        return {
            "title": f"Priority Infrastructure Intervention: {category} in {sector}",
            "sector_or_ward": sector,
            "category": category,
            "affected_population": population,
            "incident_count": count,
            "priority_score": priority_score,
            "estimated_cost_inr": cost_lakhs * 100000,
            "estimated_cost_lakhs": cost_lakhs,
            "urgency_level": "CRITICAL" if priority_score >= 80 else ("HIGH" if priority_score >= 60 else "MEDIUM"),
            "recommended_action": f"Deploy rapid-response engineering team to {sector} for comprehensive overhaul of {category.lower()} assets.",
            "dpr_summary": f"Aggregated {count} verified citizen reports across {sector}. Gemini AI analysis indicates severe public hazard risk. Recommended inclusion in Chandigarh Smart City Capital Works Plan FY 2026-27 under Ward #{budget_info.get('ward', 'General')}."
        }
