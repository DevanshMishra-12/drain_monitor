"""
GenAI City Intelligence Engine extracting structured flood events from unstructured human reports.
"""

import re
import datetime
from pydantic import BaseModel, Field
from drain_monitor.config import LANDMARKS

class CityReportEvent(BaseModel):
    location: str = Field(..., description="Identified landmark or road segment")
    event: str = Field(..., description="Classified event category (e.g. drain_blockage, construction, waterlogging)")
    event_type: str = Field(..., description="Classified event category alias")
    blockage_ratio: float = Field(default=0.0, description="Estimated drain blockage ratio 0.0-1.0")
    road_capacity_reduction: float = Field(default=0.0, description="Estimated road capacity reduction 0.0-1.0")
    confidence: float = Field(default=0.88, description="Confidence score of extracted report")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now().isoformat(), description="ISO timestamp")
    source: str = Field(default="citizen_report", description="Information source classification")
    raw_text: str = Field(..., description="Original input report string")

class GenAICityIntelligenceEngine:
    """
    Parses unstructured text/citizen reports into structured actionable flood events.
    """
    def __init__(self):
        self.landmarks = list(LANDMARKS.keys())

    def process_report(self, text_report: str) -> CityReportEvent:
        """
        Parses human report text into structured JSON event payload.
        """
        report_lower = text_report.lower()

        # Step 1: Identify Location
        detected_location = "Mandi House"  # Default fallback
        for lm in self.landmarks:
            parts = lm.lower().split()
            if any(part in report_lower for part in parts if len(part) > 3):
                detected_location = lm
                break
        
        if "rajiv" in report_lower or "cp" in report_lower or "connaught" in report_lower:
            detected_location = "Rajiv Chowk Outer Circle"
        elif "barakhamba" in report_lower:
            detected_location = "Barakhamba Rd Metro"
        elif "tolstoy" in report_lower:
            detected_location = "Tolstoy Marg Junction"
        elif "janpath" in report_lower:
            detected_location = "Janpath Junction"
        elif "kg" in report_lower or "kasturba" in report_lower:
            detected_location = "KG Marg Junction"

        # Step 2: Identify Event Type
        event_type = "waterlogging_report"
        blockage_ratio = 0.0
        road_reduction = 0.0

        if any(w in report_lower for w in ["clog", "block", "choke", "garbage", "trash", "plastic"]):
            event_type = "drain_blockage"
            blockage_ratio = 0.70
            road_reduction = 0.20
        elif any(w in report_lower for w in ["constrain", "construction", "work", "digging", "single lane", "closed"]):
            event_type = "construction"
            blockage_ratio = 0.30
            road_reduction = 0.50
        elif any(w in report_lower for w in ["overflow", "flood", "submerged", "deep water", "high water"]):
            event_type = "severe_waterlogging"
            blockage_ratio = 0.85
            road_reduction = 0.60
        elif any(w in report_lower for w in ["pump", "cleared", "drained"]):
            event_type = "pump_intervention"
            blockage_ratio = 0.0
            road_reduction = 0.0

        # Refine severity percentage if numbers are mentioned (e.g. "60% blocked" or "half closed")
        pct_match = re.search(r'(\d+)\s*%', report_lower)
        if pct_match:
            pct_val = float(pct_match.group(1)) / 100.0
            if "block" in report_lower or "clog" in report_lower:
                blockage_ratio = min(1.0, pct_val)
            else:
                road_reduction = min(1.0, pct_val)

        return CityReportEvent(
            location=detected_location,
            event=event_type,
            event_type=event_type,
            blockage_ratio=round(blockage_ratio, 2),
            road_capacity_reduction=round(road_reduction, 2),
            confidence=0.88,
            source="citizen_report",
            raw_text=text_report
        )
