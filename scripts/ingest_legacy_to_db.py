"""
Phase 1 Ingestion Script:
Streams dynamic_supply_chain_logistics_dataset.csv in batches
and populates the shipment_telemetry table in PostgreSQL.
"""
import os
import sys
import time
import pandas as pd
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.db.connection import engine, Base, SessionLocal
from src.db.models import ShipmentTelemetry

CSV_PATH = os.path.join("data", "legacy", "dynamic_supply_chain_logistics_dataset.csv")
CHUNK_SIZE = 5000

def run_legacy_ingestion():
    if not os.path.exists(CSV_PATH):
        print(f"[ERROR] Dataset file not found at: {CSV_PATH}")
        return

    print("[INFO] Step 1: Initializing PostgreSQL database tables...")
    Base.metadata.create_all(bind=engine)
    print("[SUCCESS] Table 'shipment_telemetry' created or verified in PostgreSQL.")

    db = SessionLocal()
    try:
        existing_count = db.query(ShipmentTelemetry).count()
        if existing_count > 0:
            print(f"[WARNING] Table already contains {existing_count:,} records.")
            print("[INFO] Cleaning existing records to avoid duplicates...")
            db.query(ShipmentTelemetry).delete()
            db.commit()

        print(f"[INFO] Step 2: Streaming dataset from {CSV_PATH} in batches of {CHUNK_SIZE:,} rows...")
        start_time = time.time()
        total_inserted = 0

        # Read CSV in chunks for memory-safe streaming
        for chunk_idx, chunk in enumerate(pd.read_csv(CSV_PATH, chunksize=CHUNK_SIZE), start=1):
            # Parse timestamps
            chunk['timestamp'] = pd.to_datetime(chunk['timestamp'], errors='coerce')

            # Replace NaNs with None for PostgreSQL compatibility
            chunk = chunk.where(pd.notnull(chunk), None)

            # Convert rows to ShipmentTelemetry model instances
            records = []
            for _, row in chunk.iterrows():
                record = ShipmentTelemetry(
                    timestamp=row['timestamp'],
                    vehicle_gps_latitude=row['vehicle_gps_latitude'],
                    vehicle_gps_longitude=row['vehicle_gps_longitude'],
                    fuel_consumption_rate=row['fuel_consumption_rate'],
                    eta_variation_hours=row['eta_variation_hours'],
                    traffic_congestion_level=row['traffic_congestion_level'],
                    warehouse_inventory_level=row['warehouse_inventory_level'],
                    loading_unloading_time=row['loading_unloading_time'],
                    handling_equipment_availability=row['handling_equipment_availability'],
                    order_fulfillment_status=row['order_fulfillment_status'],
                    weather_condition_severity=row['weather_condition_severity'],
                    port_congestion_level=row['port_congestion_level'],
                    shipping_costs=row['shipping_costs'],
                    supplier_reliability_score=row['supplier_reliability_score'],
                    lead_time_days=row['lead_time_days'],
                    historical_demand=row['historical_demand'],
                    iot_temperature=row['iot_temperature'],
                    cargo_condition_status=row['cargo_condition_status'],
                    route_risk_level=row['route_risk_level'],
                    customs_clearance_time=row['customs_clearance_time'],
                    driver_behavior_score=row['driver_behavior_score'],
                    fatigue_monitoring_score=row['fatigue_monitoring_score'],
                    disruption_likelihood_score=row['disruption_likelihood_score'],
                    delay_probability=row['delay_probability'],
                    risk_classification=row['risk_classification'],
                    delivery_time_deviation=row['delivery_time_deviation']
                )
                records.append(record)

            db.bulk_save_objects(records)
            db.commit()
            total_inserted += len(records)
            print(f"  -> Ingested batch {chunk_idx}: {total_inserted:,} total records committed...")

        elapsed = time.time() - start_time
        print(f"\n[DONE] Ingestion Complete! Successfully inserted {total_inserted:,} records into PostgreSQL in {elapsed:.2f} seconds.")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Ingestion failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_legacy_ingestion()
