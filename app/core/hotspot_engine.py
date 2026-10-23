from typing import List, Dict, Any
from collections import defaultdict
import math

class HotspotEngine:
    """
    Geographic & categorical clustering engine for municipal infrastructure requests.
    Calculates demand hotspots and sector health scores across Tricity.
    """

    @staticmethod
    def compute_hotspots(grievances: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        clusters = defaultdict(list)
        
        for g in grievances:
            key = (g.get("sector", "Sector 17"), g.get("category", "Roads & Traffic"))
            clusters[key].append(g)

        hotspots = []
        cluster_counter = 1

        for (sector, category), items in clusters.items():
            count = len(items)
            avg_urgency = sum(i.get("urgency_score", 5) for i in items) / max(1, count)
            center_lat = sum(i.get("lat", 30.7398) for i in items) / max(1, count)
            center_lng = sum(i.get("lng", 76.7827) for i in items) / max(1, count)

            # A hotspot is surfaced for every reported sector issue
            if count >= 1:
                hotspots.append({
                    "cluster_id": f"HOTSPOT-TRICITY-{cluster_counter:03d}",
                    "sector": sector,
                    "category": category,
                    "incident_count": count,
                    "avg_urgency": round(avg_urgency, 1),
                    "center_lat": round(center_lat, 5),
                    "center_lng": round(center_lng, 5),
                    "summary": f"{count} reported issues concerning {category} in {sector} (Avg Urgency: {round(avg_urgency, 1)}/10)",
                    "sample_grievances": [i.get("summary", "") for i in items[:3]]
                })
                cluster_counter += 1

        # Sort hotspots by incident_count * avg_urgency descending
        hotspots.sort(key=lambda h: h["incident_count"] * h["avg_urgency"], reverse=True)
        return hotspots

    @staticmethod
    def compute_sector_metrics(grievances: List[Dict[str, Any]], sector_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        sector_groups = defaultdict(list)
        for g in grievances:
            sec = g.get("sector", "Sector 17")
            sector_groups[sec].append(g)

        metrics = []
        for sec, meta in sector_metadata.items():
            items = sector_groups.get(sec, [])
            total = len(items)
            open_count = sum(1 for i in items if i.get("status") != "RESOLVED")
            
            # Dominant category
            cat_counts = defaultdict(int)
            for i in items:
                cat_counts[i.get("category", "General Public Infrastructure")] += 1
            dom_cat = max(cat_counts.items(), key=lambda x: x[1])[0] if cat_counts else "None Reported"

            # Infrastructure Health Score: 100 - penalties for open issues & urgency
            penalty = sum(i.get("urgency_score", 5) * 1.8 for i in items if i.get("status") != "RESOLVED")
            health_score = max(20.0, round(100.0 - penalty, 1))

            metrics.append({
                "sector": sec,
                "ward_number": meta.get("ward"),
                "population": meta.get("population", 20000),
                "zone": meta.get("zone", "Central"),
                "lat": meta.get("lat"),
                "lng": meta.get("lng"),
                "total_incidents": total,
                "open_incidents": open_count,
                "infrastructure_health_score": health_score,
                "dominant_category": dom_cat,
                "allocated_budget_lakhs": round(meta.get("population", 20000) * 0.004, 1)  # approx ₹400 per capita capital fund
            })

        # Sort so sectors with most incidents appear first
        metrics.sort(key=lambda m: (m["open_incidents"], 100 - m["infrastructure_health_score"]), reverse=True)
        return metrics
