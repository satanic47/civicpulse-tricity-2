import re
from typing import Optional, Tuple, Dict, Any

# Canonical coordinate mapping for Chandigarh, Mohali, and Panchkula
TRICITY_SECTORS: Dict[str, Dict[str, Any]] = {
    "Sector 1": {"lat": 30.7583, "lng": 76.8058, "ward": 1, "zone": "North", "population": 4200, "landmarks": ["Capitol Complex", "High Court", "Secretariat"]},
    "Sector 2": {"lat": 30.7547, "lng": 76.7972, "ward": 1, "zone": "North", "population": 3800, "landmarks": ["Governor House"]},
    "Sector 3": {"lat": 30.7511, "lng": 76.7886, "ward": 1, "zone": "North", "population": 4100, "landmarks": ["War Memorial"]},
    "Sector 4": {"lat": 30.7475, "lng": 76.7800, "ward": 1, "zone": "North", "population": 5200, "landmarks": ["MLA Hostels"]},
    "Sector 5": {"lat": 30.7590, "lng": 76.8120, "ward": 1, "zone": "North", "population": 4600, "landmarks": ["Sukhna Enclave"]},
    "Sector 6": {"lat": 30.7630, "lng": 76.8200, "ward": 2, "zone": "East", "population": 6500, "landmarks": ["Sukhna Lake", "Golf Club"]},
    "Sector 7": {"lat": 30.7320, "lng": 76.8040, "ward": 2, "zone": "East", "population": 12500, "landmarks": ["Madhya Marg Market"]},
    "Sector 8": {"lat": 30.7350, "lng": 76.7960, "ward": 2, "zone": "East", "population": 14200, "landmarks": ["Inner Market", "Dav College"]},
    "Sector 9": {"lat": 30.7420, "lng": 76.7870, "ward": 2, "zone": "North", "population": 11800, "landmarks": ["Police HQ", "Carmel Convent"]},
    "Sector 10": {"lat": 30.7490, "lng": 76.7790, "ward": 3, "zone": "Central", "population": 10500, "landmarks": ["Government Museum", "Art College"]},
    "Sector 11": {"lat": 30.7560, "lng": 76.7710, "ward": 3, "zone": "Central", "population": 16000, "landmarks": ["PG Govt College for Boys"]},
    "Sector 12": {"lat": 30.7640, "lng": 76.7760, "ward": 3, "zone": "North", "population": 8500, "landmarks": ["PGI", "PEC University"]},
    "Sector 14": {"lat": 30.7600, "lng": 76.7640, "ward": 3, "zone": "West", "population": 19000, "landmarks": ["Panjab University", "Student Centre"]},
    "Sector 15": {"lat": 30.7510, "lng": 76.7710, "ward": 4, "zone": "West", "population": 28500, "landmarks": ["Patel Market", "DCM School"]},
    "Sector 16": {"lat": 30.7440, "lng": 76.7730, "ward": 4, "zone": "Central", "population": 15500, "landmarks": ["Zakir Hussain Rose Garden", "Cricket Stadium", "GMSH 16"]},
    "Sector 17": {"lat": 30.7398, "lng": 76.7827, "ward": 5, "zone": "Central", "population": 3500, "landmarks": ["Sector 17 Plaza", "ISBT 17", "DC Office"]},
    "Sector 18": {"lat": 30.7310, "lng": 76.7910, "ward": 5, "zone": "Central", "population": 14000, "landmarks": ["Tagore Theatre", "Rotary Club"]},
    "Sector 19": {"lat": 30.7240, "lng": 76.7990, "ward": 6, "zone": "East", "population": 29000, "landmarks": ["Palika Bazaar", "Sadhu Vaswani School"]},
    "Sector 20": {"lat": 30.7170, "lng": 76.7920, "ward": 6, "zone": "East", "population": 34000, "landmarks": ["Sector 20 Mosque", "Govt Girls Model School"]},
    "Sector 21": {"lat": 30.7230, "lng": 76.7830, "ward": 7, "zone": "Central", "population": 21000, "landmarks": ["Aroma Chowk", "Sector 21 Market"]},
    "Sector 22": {"lat": 30.7300, "lng": 76.7740, "ward": 7, "zone": "Central", "population": 36000, "landmarks": ["Shastri Market", "Kiran Cinema", "Sector 22 Mobile Market"]},
    "Sector 23": {"lat": 30.7370, "lng": 76.7660, "ward": 8, "zone": "West", "population": 22000, "landmarks": ["Children Traffic Park", "All India Radio"]},
    "Sector 24": {"lat": 30.7430, "lng": 76.7580, "ward": 8, "zone": "West", "population": 25000, "landmarks": ["Dhanas Border", "Indira Holiday Home"]},
    "Sector 25": {"lat": 30.7500, "lng": 76.7500, "ward": 8, "zone": "West", "population": 21000, "landmarks": ["Panjab University South Campus", "Rally Ground"]},
    "Sector 26": {"lat": 30.7260, "lng": 76.8120, "ward": 9, "zone": "East", "population": 18000, "landmarks": ["Grain Market", "St. Johns School", "Timber Market"]},
    "Sector 27": {"lat": 30.7190, "lng": 76.8070, "ward": 9, "zone": "East", "population": 22000, "landmarks": ["Press Site", "Sanatan Dharma Mandir"]},
    "Sector 28": {"lat": 30.7120, "lng": 76.8020, "ward": 9, "zone": "East", "population": 24000, "landmarks": ["Motor Market 28", "Govt Press"]},
    "Sector 29": {"lat": 30.7050, "lng": 76.7940, "ward": 10, "zone": "Industrial", "population": 26000, "landmarks": ["Iron Market", "Ordnance Cable Factory"]},
    "Sector 30": {"lat": 30.7110, "lng": 76.7860, "ward": 10, "zone": "Central", "population": 27000, "landmarks": ["CSIO", "TERI"]},
    "Sector 31": {"lat": 30.7000, "lng": 76.7870, "ward": 11, "zone": "South", "population": 26500, "landmarks": ["BRD Air Force Station", "3BRD Market"]},
    "Sector 32": {"lat": 30.7080, "lng": 76.7780, "ward": 11, "zone": "South", "population": 28000, "landmarks": ["GMCH 32 Hospital", "SD College"]},
    "Sector 33": {"lat": 30.7150, "lng": 76.7700, "ward": 12, "zone": "South", "population": 19000, "landmarks": ["Terraced Garden", "State Library 34 Border"]},
    "Sector 34": {"lat": 30.7220, "lng": 76.7620, "ward": 12, "zone": "Central", "population": 14000, "landmarks": ["Sub-City Centre 34", "Coaching Hub", "Exhibition Ground", "Gurudwara 34"]},
    "Sector 35": {"lat": 30.7290, "lng": 76.7540, "ward": 13, "zone": "South-West", "population": 25000, "landmarks": ["Sector 35 Hotel Strip", "JW Marriott Chowk", "Inner Market 35C"]},
    "Sector 36": {"lat": 30.7350, "lng": 76.7460, "ward": 13, "zone": "West", "population": 18500, "landmarks": ["MCM DAV College", "Fragrance Garden"]},
    "Sector 37": {"lat": 30.7420, "lng": 76.7380, "ward": 14, "zone": "West", "population": 31000, "landmarks": ["Community Centre 37", "Market 37D"]},
    "Sector 38": {"lat": 30.7480, "lng": 76.7300, "ward": 14, "zone": "West", "population": 33000, "landmarks": ["Sector 38 West", "Shahpur Colony"]},
    "Sector 40": {"lat": 30.7300, "lng": 76.7260, "ward": 15, "zone": "South-West", "population": 32000, "landmarks": ["Badheri Market", "Sector 40 Community Centre"]},
    "Sector 41": {"lat": 30.7360, "lng": 76.7340, "ward": 15, "zone": "South-West", "population": 29000, "landmarks": ["Krishna Market 41", "Govt Model School"]},
    "Sector 42": {"lat": 30.7240, "lng": 76.7410, "ward": 16, "zone": "South", "population": 21000, "landmarks": ["New Lake 42", "Post Graduate College for Girls 42", "Hockey Stadium"]},
    "Sector 43": {"lat": 30.7160, "lng": 76.7490, "ward": 16, "zone": "South", "population": 23000, "landmarks": ["ISBT 43 Bus Stand", "District Courts Complex"]},
    "Sector 44": {"lat": 30.7090, "lng": 76.7570, "ward": 17, "zone": "South", "population": 28000, "landmarks": ["Sector 44 Market", "St. Xaviers"]},
    "Sector 45": {"lat": 30.7020, "lng": 76.7650, "ward": 17, "zone": "South", "population": 42000, "landmarks": ["Burail Village", "Sector 45 Hospital"]},
    "Sector 46": {"lat": 30.6950, "lng": 76.7730, "ward": 18, "zone": "South", "population": 31000, "landmarks": ["Post Graduate Govt College 46", "Sector 46 Market"]},
    "Sector 47": {"lat": 30.6880, "lng": 76.7810, "ward": 18, "zone": "South", "population": 27000, "landmarks": ["Faidan Border", "Sector 47 Community Centre"]},
    "Sector 48": {"lat": 30.6820, "lng": 76.7720, "ward": 19, "zone": "South", "population": 22000, "landmarks": ["Motor Market 48", "Society Flats"]},
    "Sector 49": {"lat": 30.6880, "lng": 76.7640, "ward": 19, "zone": "South", "population": 24000, "landmarks": ["Progressive Society", "Advocate Society"]},
    "Sector 50": {"lat": 30.6950, "lng": 76.7560, "ward": 20, "zone": "South", "population": 21000, "landmarks": ["Cooperative Societies 50"]},
    "Sector 51": {"lat": 30.7020, "lng": 76.7480, "ward": 20, "zone": "South", "population": 19000, "landmarks": ["Model Jail Border", "Chandigarh Housing Board Flats"]},
    "Sector 52": {"lat": 30.7080, "lng": 76.7400, "ward": 21, "zone": "South-West", "population": 36000, "landmarks": ["Kajheri Village", "Sector 52 Garden"]},
    "Sector 53": {"lat": 30.7140, "lng": 76.7320, "ward": 21, "zone": "South-West", "population": 12000, "landmarks": ["Nehru Park 53", "Mohali Border"]},
    "Sector 54": {"lat": 30.7200, "lng": 76.7240, "ward": 21, "zone": "South-West", "population": 18000, "landmarks": ["Furniture Market 54", "Badheri Barrier"]},
    # Mohali (SAS Nagar)
    "Phase 7 Mohali": {"lat": 30.7055, "lng": 76.7125, "ward": 101, "zone": "Mohali", "population": 38000, "landmarks": ["Phase 7 Market", "Khabar Chowk", "Phase 7 Industrial"]},
    "Phase 3B2 Mohali": {"lat": 30.7180, "lng": 76.7190, "ward": 102, "zone": "Mohali", "population": 34000, "landmarks": ["Phase 3B2 Food Street", "Rose Garden Mohali"]},
    "Phase 5 Mohali": {"lat": 30.7120, "lng": 76.7080, "ward": 103, "zone": "Mohali", "population": 29000, "landmarks": ["Civil Hospital Mohali", "Phase 5 Market"]},
    "Sector 70 Mohali": {"lat": 30.6960, "lng": 76.7200, "ward": 104, "zone": "Mohali", "population": 31000, "landmarks": ["Mataur Village", "Sector 70 Park"]},
    "Sector 62 Mohali (Phase 8)": {"lat": 30.6900, "lng": 76.7350, "ward": 105, "zone": "Mohali", "population": 25000, "landmarks": ["PCA Stadium", "Fortis Hospital Mohali"]},
    # Panchkula
    "Sector 5 Panchkula": {"lat": 30.6920, "lng": 76.8520, "ward": 201, "zone": "Panchkula", "population": 28000, "landmarks": ["Indradhanush Auditorium", "Town Park 5", "Yavanika Park"]},
    "Sector 7 Panchkula": {"lat": 30.6990, "lng": 76.8450, "ward": 202, "zone": "Panchkula", "population": 26000, "landmarks": ["Sector 7 Market Panchkula"]},
    "Sector 14 Panchkula": {"lat": 30.6850, "lng": 76.8600, "ward": 203, "zone": "Panchkula", "population": 30000, "landmarks": ["Govt College Panchkula", "Rally Ground Panchkula"]},
    "Sector 20 Panchkula": {"lat": 30.6650, "lng": 76.8550, "ward": 204, "zone": "Panchkula", "population": 45000, "landmarks": ["Ashiana Flats", "Group Housing Societies"]},
}

# Default Tricity center (Sector 17 Plaza, Chandigarh)
DEFAULT_CENTER = {"lat": 30.7398, "lng": 76.7827, "sector": "Sector 17"}

def resolve_sector(text: str) -> Dict[str, Any]:
    """
    Intelligently identifies sector, zone, and coordinates from raw complaint text,
    landmark mentions, or explicit sector numbers in Hindi, Punjabi, or English.
    """
    clean_text = text.lower()

    # 1. Check for explicit Mohali phases
    phase_match = re.search(r'phase\s*([0-9]{1,2}|3b2|3b-2|vii|v|viii)', clean_text)
    if phase_match:
        p_val = phase_match.group(1).upper()
        if "3B2" in p_val or "3B-2" in p_val:
            sec = "Phase 3B2 Mohali"
            return {"sector": sec, **TRICITY_SECTORS[sec]}
        elif p_val in ["7", "VII"]:
            sec = "Phase 7 Mohali"
            return {"sector": sec, **TRICITY_SECTORS[sec]}
        elif p_val in ["5", "V"]:
            sec = "Phase 5 Mohali"
            return {"sector": sec, **TRICITY_SECTORS[sec]}
        elif p_val in ["8", "VIII"]:
            sec = "Sector 62 Mohali (Phase 8)"
            return {"sector": sec, **TRICITY_SECTORS[sec]}

    # 2. Check for explicit Panchkula sectors
    pk_match = re.search(r'panchkula.*?sector\s*([0-9]{1,2})|sector\s*([0-9]{1,2}).*?panchkula', clean_text)
    if pk_match:
        s_num = pk_match.group(1) or pk_match.group(2)
        target = f"Sector {s_num} Panchkula"
        if target in TRICITY_SECTORS:
            return {"sector": target, **TRICITY_SECTORS[target]}

    # 3. Check for explicit Sector numbers (e.g., "sector 22", "sec 35", "ਸੈਕਟਰ 22", "सेक्टर 35")
    # Supports Devanagari digits or numbers
    sec_match = re.search(r'(?:sector|sec|ਸੈਕਟਰ|सेक्टर)\s*[-:]?\s*([0-9]{1,2})', clean_text)
    if sec_match:
        s_num = sec_match.group(1)
        target = f"Sector {s_num}"
        if target in TRICITY_SECTORS:
            return {"sector": target, **TRICITY_SECTORS[target]}

    # 4. Check for landmark associations
    for sec_name, data in TRICITY_SECTORS.items():
        for lm in data.get("landmarks", []):
            if lm.lower() in clean_text:
                return {"sector": sec_name, **data}

    # 5. Mohali/Panchkula general match
    if "mohali" in clean_text or "sas nagar" in clean_text:
        sec = "Phase 7 Mohali"
        return {"sector": sec, **TRICITY_SECTORS[sec]}
    if "panchkula" in clean_text:
        sec = "Sector 5 Panchkula"
        return {"sector": sec, **TRICITY_SECTORS[sec]}

    # Default fallback to Sector 17 Central
    return {"sector": "Sector 17", **TRICITY_SECTORS["Sector 17"]}

def get_all_sector_metadata() -> Dict[str, Dict[str, Any]]:
    return TRICITY_SECTORS
