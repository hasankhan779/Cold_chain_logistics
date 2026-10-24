"""
LangGraph Agent Tools:
1. PostgreSQL Telemetry Query Tool (Queries 32,065 records for breaches, delays, congestion)
2. Pinecone Vector SOP Search Tool (Retrieves SOP v2.4 rules and mitigations)
3. Open-Meteo Weather Tool (Live ambient transit temperature along GPS coordinates)
"""
import json
from langchain_core.tools import tool
from src.db.connection import SessionLocal
from src.db.repository import LogisticsRepository
from src.rag.vector_store import VectorStoreService
from src.services.weather_service import WeatherService

vector_service = VectorStoreService()

@tool
def lookup_telemetry_record(record_id: int) -> str:
    """Fetch complete telemetry data for a specific shipment/vehicle record by its integer ID from PostgreSQL."""
    db = SessionLocal()
    try:
        repo = LogisticsRepository(db)
        record = repo.get_telemetry_by_id(record_id)
        if not record:
            return f"No telemetry record found with ID: {record_id}"

        return json.dumps({
            "record_id": record.id,
            "timestamp": str(record.timestamp),
            "iot_temperature_c": record.iot_temperature,
            "is_temperature_breach": record.is_temperature_breach,
            "port_congestion_level": record.port_congestion_level,
            "is_port_congested": record.is_port_congested,
            "traffic_congestion_level": record.traffic_congestion_level,
            "eta_variation_hours": record.eta_variation_hours,
            "delay_probability": record.delay_probability,
            "risk_classification": record.risk_classification,
            "requires_tier2_escalation": record.requires_tier2_escalation,
            "vehicle_gps_latitude": record.vehicle_gps_latitude,
            "vehicle_gps_longitude": record.vehicle_gps_longitude
        }, indent=2)
    finally:
        db.close()

@tool
def query_fleet_breaches_and_alerts(alert_type: str = "all", limit: int = 5) -> str:
    """
    Query PostgreSQL for active fleet anomalies.
    alert_type can be:
    - 'temperature': shipments with iot_temperature > 4.0°C
    - 'congestion': routes with port_congestion_level > 7.0
    - 'escalations': High Risk shipments with delay_probability > 0.65
    - 'all': returns an overview of latest anomalies across all three categories
    """
    db = SessionLocal()
    try:
        repo = LogisticsRepository(db)
        results = {}

        if alert_type in ["temperature", "all"]:
            temp_breaches = repo.get_active_excursions(limit=limit)
            results["temperature_breaches"] = [
                {
                    "id": r.id,
                    "temp_c": r.iot_temperature,
                    "timestamp": str(r.timestamp),
                    "gps": (r.vehicle_gps_latitude, r.vehicle_gps_longitude)
                } for r in temp_breaches
            ]

        if alert_type in ["congestion", "all"]:
            congested = repo.get_congested_ports(limit=limit)
            results["port_congestion_alerts"] = [
                {
                    "id": r.id,
                    "congestion_level": r.port_congestion_level,
                    "timestamp": str(r.timestamp),
                    "gps": (r.vehicle_gps_latitude, r.vehicle_gps_longitude)
                } for r in congested
            ]

        if alert_type in ["escalations", "all"]:
            escalations = repo.get_high_risk_escalations(limit=limit)
            results["tier2_escalations"] = [
                {
                    "id": r.id,
                    "risk": r.risk_classification,
                    "delay_probability": r.delay_probability,
                    "timestamp": str(r.timestamp)
                } for r in escalations
            ]

        return json.dumps(results, indent=2)
    finally:
        db.close()

@tool
def search_cold_chain_sops(query: str) -> str:
    """
    Search Southern California Logistics Standard Operating Procedures (SOP v2.4) in Pinecone.
    Retrieves the single most relevant protocol or threshold.
    """
    results = vector_service.search_sops(query, top_k=1)
    return json.dumps(results, indent=2)

@tool
def fetch_ambient_weather(latitude: float, longitude: float) -> str:
    """
    Fetch live ambient temperature, humidity, and weather conditions from Open-Meteo
    for the vehicle's transit GPS coordinates.
    """
    result = WeatherService.get_route_weather(latitude, longitude)
    return json.dumps(result, indent=2)

AGENT_TOOLS = [
    lookup_telemetry_record,
    query_fleet_breaches_and_alerts,
    search_cold_chain_sops,
    fetch_ambient_weather
]
