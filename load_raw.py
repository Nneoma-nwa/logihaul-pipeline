import os
import csv
import psycopg


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.getenv("LOGIHAUL_DATA_DIR", os.path.join(PROJECT_ROOT, "data"))

DB_CONFIG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": int(os.getenv("PGPORT", "5432")),
    "dbname": os.getenv("PGDATABASE", "logihaul"),
    "user": os.getenv("PGUSER", "logihaul"),
    "password": os.getenv("PGPASSWORD", "Admin"),
}


TABLES = {
    "drivers": [
        "driver_id",
        "first_name",
        "last_name",
        "phone_number",
        "license_number",
        "license_expiry",
        "hire_date",
        "state_of_origin",
        "status",
    ],
    "vehicles": [
        "vehicle_id",
        "plate_number",
        "vehicle_type",
        "make",
        "model",
        "year",
        "capacity_kg",
        "acquisition_date",
        "status",
    ],
    "routes": [
        "route_id",
        "origin_city",
        "destination_city",
        "distance_km",
        "estimated_duration_hrs",
    ],
    "trips": [
        "trip_id",
        "vehicle_id",
        "driver_id",
        "route_id",
        "start_time",
        "end_time",
        "distance_km",
        "status",
    ],
    "deliveries": [
        "delivery_id",
        "trip_id",
        "customer_name",
        "delivery_address",
        "scheduled_time",
        "actual_delivery_time",
        "status",
        "customer_phone",
    ],
    "maintenance_events": [
        "maintenance_id",
        "vehicle_id",
        "maintenance_date",
        "maintenance_type",
        "cost",
        "odometer_reading",
    ],
    "operating_costs": [
        "cost_id",
        "trip_id",
        "vehicle_id",
        "cost_type",
        "amount",
        "cost_date",
    ],
}


LOAD_ORDER = [
    "drivers",
    "vehicles",
    "routes",
    "trips",
    "deliveries",
    "maintenance_events",
    "operating_costs",
]


def load_table(cur, table_name, columns):
    csv_path = os.path.join(DATA_DIR, f"{table_name}.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    column_list = ", ".join(columns)

    copy_sql = f"""
        COPY raw.{table_name} ({column_list})
        FROM STDIN
        WITH (FORMAT CSV, HEADER TRUE, NULL '');
    """

    with open(csv_path, "r", newline="", encoding="utf-8") as csv_file:
        with cur.copy(copy_sql) as copy:
            while data := csv_file.read(1024 * 1024):
                copy.write(data)

    with open(csv_path, "r", newline="", encoding="utf-8") as csv_file:
        row_count = sum(1 for _ in csv_file) - 1

    print(f"Loaded raw.{table_name}: {row_count:,} rows")


def main():
    print("Starting raw data ingestion...")
    print(f"Source directory: {DATA_DIR}")

    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:

            tables = ", ".join(
                f"raw.{table}" for table in LOAD_ORDER
            )

            print("Truncating raw tables...")
            cur.execute(f"TRUNCATE {tables} CASCADE;")

            for table_name in LOAD_ORDER:
                load_table(
                    cur,
                    table_name,
                    TABLES[table_name],
                )

        conn.commit()

    print("Raw data ingestion completed successfully.")


if __name__ == "__main__":
    main()
