import pytest
from drain_monitor.genai.intelligence import GenAICityIntelligenceEngine

def test_genai_city_intelligence():
    engine = GenAICityIntelligenceEngine()

    report1 = "Drain clogged near Barakhamba metro gate 2 with garbage plastic bags."
    res1 = engine.process_report(report1)
    assert res1.location == "Barakhamba Rd Metro"
    assert res1.event_type == "drain_blockage"
    assert res1.blockage_ratio > 0.0

    report2 = "Construction works at Tolstoy Marg reduced road to single lane."
    res2 = engine.process_report(report2)
    assert res2.location == "Tolstoy Marg Junction"
    assert res2.event_type == "construction"
    assert res2.road_capacity_reduction > 0.0
