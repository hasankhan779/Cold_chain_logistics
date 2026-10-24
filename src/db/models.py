"""
SQLAlchemy ORM models aligned with the dynamic supply chain logistics dataset.
Captures all 26 telemetry, cold-chain IoT temperature, route congestion, and risk fields.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Index
from src.db.connection import Base

class ShipmentTelemetry(Base):
    """
    Represents a dynamic telemetry and status snapshot of a cold-chain logistics transit record.
    Matches the columns from dynamic_supply_chain_logistics_dataset.csv.
    """
    __tablename__ = "shipment_telemetry"

    # Primary key & tracking
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True)

    # GPS coordinates
    vehicle_gps_latitude = Column(Float, nullable=False)
    vehicle_gps_longitude = Column(Float, nullable=False)

    # Cold-chain IoT sensor telemetry
    iot_temperature = Column(Float, nullable=False, index=True)  # Reefer cargo temp in °C
    cargo_condition_status = Column(Float, nullable=True)

    # Congestion & traffic metrics
    traffic_congestion_level = Column(Float, nullable=True)
    port_congestion_level = Column(Float, nullable=True, index=True)  # Key field for SOP v2.4

    # ETA & transit delays
    eta_variation_hours = Column(Float, nullable=True)
    delivery_time_deviation = Column(Float, nullable=True)
    lead_time_days = Column(Float, nullable=True)
    loading_unloading_time = Column(Float, nullable=True)
    customs_clearance_time = Column(Float, nullable=True)

    # Risk metrics & classification (SOP triggers)
    delay_probability = Column(Float, nullable=True, index=True)      # Critical for >0.65 threshold
    risk_classification = Column(String(50), nullable=True, index=True) # E.g., 'High Risk'
    route_risk_level = Column(Float, nullable=True)
    disruption_likelihood_score = Column(Float, nullable=True)
    weather_condition_severity = Column(Float, nullable=True)

    # Operational & driver efficiency
    fuel_consumption_rate = Column(Float, nullable=True)
    driver_behavior_score = Column(Float, nullable=True)
    fatigue_monitoring_score = Column(Float, nullable=True)
    handling_equipment_availability = Column(Float, nullable=True)
    warehouse_inventory_level = Column(Float, nullable=True)
    order_fulfillment_status = Column(Float, nullable=True)
    shipping_costs = Column(Float, nullable=True)
    supplier_reliability_score = Column(Float, nullable=True)
    historical_demand = Column(Float, nullable=True)

    # SOP v2.4 helper properties for business logic
    @property
    def is_temperature_breach(self) -> bool:
        """SOP v2.4 Section 1: Fresh perishables threshold is 4.0°C."""
        return self.iot_temperature is not None and self.iot_temperature > 4.0

    @property
    def is_port_congested(self) -> bool:
        """SOP v2.4 Section 2: Port of Long Beach/LA severity threshold is > 7.0."""
        return self.port_congestion_level is not None and self.port_congestion_level > 7.0

    @property
    def requires_tier2_escalation(self) -> bool:
        """SOP v2.4 Section 3: High Risk AND delay probability > 0.65."""
        is_high_risk = self.risk_classification and "high" in self.risk_classification.lower()
        high_delay = self.delay_probability is not None and self.delay_probability > 0.65
        return is_high_risk and high_delay

    def __repr__(self):
        return (
            f"<ShipmentTelemetry id={self.id} temp={self.iot_temperature}°C "
            f"port_congestion={self.port_congestion_level} risk={self.risk_classification}>"
        )
