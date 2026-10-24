"""
Database query repository for logistics shipments and telemetry.
Optimized for high-speed page loads using fast indexed COUNT queries and cached limits.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, text
from src.db.models import ShipmentTelemetry

class LogisticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_telemetry_by_id(self, record_id: int) -> Optional[ShipmentTelemetry]:
        """Fetch a specific telemetry record by primary key."""
        return self.db.query(ShipmentTelemetry).filter(ShipmentTelemetry.id == record_id).first()

    def get_recent_records(self, limit: int = 15) -> List[ShipmentTelemetry]:
        """Fetch the most recent telemetry entries (low limit for fast rendering)."""
        return (
            self.db.query(ShipmentTelemetry)
            .order_by(desc(ShipmentTelemetry.id))
            .limit(limit)
            .all()
        )

    def get_active_excursions(self, temp_threshold: float = 4.0, limit: int = 15) -> List[ShipmentTelemetry]:
        """SOP v2.4 Rule 1: Temperature breaches above threshold."""
        return (
            self.db.query(ShipmentTelemetry)
            .filter(ShipmentTelemetry.iot_temperature > temp_threshold)
            .order_by(desc(ShipmentTelemetry.id))
            .limit(limit)
            .all()
        )

    def get_congested_ports(self, severity_threshold: float = 7.0, limit: int = 15) -> List[ShipmentTelemetry]:
        """SOP v2.4 Rule 2: Port congestion level > 7.0."""
        return (
            self.db.query(ShipmentTelemetry)
            .filter(ShipmentTelemetry.port_congestion_level > severity_threshold)
            .order_by(desc(ShipmentTelemetry.id))
            .limit(limit)
            .all()
        )

    def get_high_risk_escalations(self, delay_threshold: float = 0.65, limit: int = 15) -> List[ShipmentTelemetry]:
        """SOP v2.4 Rule 3: High Risk shipments with delay probability > 0.65."""
        return (
            self.db.query(ShipmentTelemetry)
            .filter(
                ShipmentTelemetry.risk_classification == "High Risk",
                ShipmentTelemetry.delay_probability > delay_threshold
            )
            .order_by(desc(ShipmentTelemetry.id))
            .limit(limit)
            .all()
        )

    def get_summary_metrics(self) -> Dict[str, Any]:
        """Fast summary metrics for the header."""
        total = self.db.query(ShipmentTelemetry).count()
        breaches = self.db.query(ShipmentTelemetry).filter(ShipmentTelemetry.iot_temperature > 4.0).count()
        congested = self.db.query(ShipmentTelemetry).filter(ShipmentTelemetry.port_congestion_level > 7.0).count()
        escalations = (
            self.db.query(ShipmentTelemetry)
            .filter(
                ShipmentTelemetry.risk_classification == "High Risk",
                ShipmentTelemetry.delay_probability > 0.65
            )
            .count()
        )
        return {
            "total_records": total,
            "temperature_breaches": breaches,
            "port_congestion_alerts": congested,
            "tier2_escalations": escalations
        }
