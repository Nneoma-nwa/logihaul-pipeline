"""
LogiHaul synthetic data generator (vectorized for scale).

Generates 7 related entities (drivers, vehicles, routes, trips, deliveries,
maintenance_events, operating_costs) for a simulated pan-Nigeria freight
fleet, then deliberately injects a controlled rate of data-quality issues
into each table and logs every injection to data_quality_log.csv.

Generation order respects FK dependencies:
    drivers, vehicles, routes  (parents, no FKs)
        -> trips               (depends on drivers, vehicles, routes)
            -> deliveries       (depends on trips)
            -> operating_costs  (depends on trips, vehicles)
    vehicles -> maintenance_events

At LogiHaul's scale (5,000 vehicles x 180 days) row-by-row Python loops are
too slow, so trip/delivery/cost generation is vectorized with numpy/pandas.
"""

import os
import random
import uuid
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)
rng = np.random.default_rng(42)

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
NUM_DRIVERS = 5_500
NUM_VEHICLES = 5_000
NUM_ROUTES = 200
SIM_MONTHS = 6
SIM_END = datetime(2026, 8, 28)
SIM_START = SIM_END - timedelta(days=30 * SIM_MONTHS)

NIGERIA_STATES = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue",
    "Borno", "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu",
    "FCT", "Gombe", "Imo", "Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi",
    "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger", "Ogun", "Ondo", "Osun",
    "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara",
]
MAJOR_CITIES = [
    "Lagos", "Kano", "Ibadan", "Abuja", "Port Harcourt", "Benin City",
    "Kaduna", "Enugu", "Onitsha", "Aba", "Warri", "Jos", "Ilorin",
    "Owerri", "Uyo", "Calabar", "Sokoto", "Maiduguri", "Abeokuta", "Zaria",
]
VEHICLE_TYPES = ["truck", "van", "trailer"]
VEHICLE_MAKES = ["MAN", "Scania", "Mercedes-Benz", "Volvo", "Isuzu", "Howo"]

data_quality_log = []


def log_issue(table, column, issue_type, rate, n_affected):
    data_quality_log.append(
        {"table": table, "column": column, "issue_type": issue_type,
         "target_rate": rate, "rows_affected": n_affected}
    )


def inject_issues(df, column, issue_type, rate, **kwargs):
    """Generic messiness injector — see issue_type list below. Vectorized."""
    n = len(df)
    n_affected = int(n * rate)
    if n_affected == 0:
        return df

    idx = df.sample(n=n_affected, random_state=random.randint(0, 999999)).index

    if issue_type == "null":
        df.loc[idx, column] = None
    elif issue_type == "bad_casing":
        choices = np.random.choice(["upper", "lower", "title"], size=n_affected)
        vals = df.loc[idx, column].astype(str)
        new_vals = [getattr(v, c)() for v, c in zip(vals, choices)]
        df.loc[idx, column] = new_vals
    elif issue_type == "negative":
        df.loc[idx, column] = -df.loc[idx, column].abs()
    elif issue_type == "duplicate_id":
        pool = df.loc[~df.index.isin(idx), column].sample(
            n=n_affected, replace=True, random_state=1
        ).values
        df.loc[idx, column] = pool
    elif issue_type == "invalid_fk":
        df.loc[idx, column] = [f"INVALID-{uuid.uuid4().hex[:8]}" for _ in range(n_affected)]
    elif issue_type == "out_of_order":
        other_column = kwargs["other_column"]
        tmp = df.loc[idx, column].copy()
        df.loc[idx, column] = df.loc[idx, other_column]
        df.loc[idx, other_column] = tmp

    log_issue(df.attrs.get("table_name", "unknown"), column, issue_type, rate, n_affected)
    return df


# ---------------------------------------------------------------------------
# 1. DRIVERS
# ---------------------------------------------------------------------------
def generate_drivers(n=NUM_DRIVERS):
    hire_dates = [fake.date_between(start_date="-5y", end_date=SIM_START) for _ in range(n)]
    df = pd.DataFrame(
        {
            "driver_id": [f"DRV-{i+1:06d}" for i in range(n)],
            "first_name": [fake.first_name() for _ in range(n)],
            "last_name": [fake.last_name() for _ in range(n)],
            "phone_number": [fake.msisdn()[:11] for _ in range(n)],
            "license_number": [f"LIC-{uuid.uuid4().hex[:10].upper()}" for _ in range(n)],
            "license_expiry": [fake.date_between(start_date=SIM_START, end_date="+3y") for _ in range(n)],
            "hire_date": hire_dates,
            "state_of_origin": rng.choice(NIGERIA_STATES, size=n),
            "status": rng.choice(["active", "suspended", "inactive"], size=n, p=[0.88, 0.05, 0.07]),
        }
    )
    df.attrs["table_name"] = "drivers"
    df = inject_issues(df, "phone_number", "null", 0.02)
    df = inject_issues(df, "state_of_origin", "bad_casing", 0.05)
    df = inject_issues(df, "license_expiry", "out_of_order", 0.01, other_column="hire_date")
    return df


# ---------------------------------------------------------------------------
# 2. VEHICLES
# ---------------------------------------------------------------------------
def generate_vehicles(n=NUM_VEHICLES):
    prefixes = rng.choice(["LAG", "ABJ", "KAN", "PHC", "IBD"], size=n)
    nums = rng.integers(100, 999, size=n)
    letters = rng.choice(list("ABCDEFGH"), size=n)
    suffix = rng.integers(10, 99, size=n)
    plates = [f"{p}-{n_}{l}{s}" for p, n_, l, s in zip(prefixes, nums, letters, suffix)]

    df = pd.DataFrame(
        {
            "vehicle_id": [f"VEH-{i+1:06d}" for i in range(n)],
            "plate_number": plates,
            "vehicle_type": rng.choice(VEHICLE_TYPES, size=n, p=[0.7, 0.15, 0.15]),
            "make": rng.choice(VEHICLE_MAKES, size=n),
            "model": [fake.bothify(text="Model-##??").upper() for _ in range(n)],
            "year": rng.integers(2010, 2026, size=n),
            "capacity_kg": rng.choice([5000, 8000, 12000, 20000, 30000], size=n),
            "acquisition_date": [fake.date_between(start_date="-8y", end_date=SIM_START) for _ in range(n)],
            "status": rng.choice(["active", "in_maintenance", "decommissioned"], size=n, p=[0.85, 0.10, 0.05]),
        }
    )
    df.attrs["table_name"] = "vehicles"
    df = inject_issues(df, "plate_number", "duplicate_id", 0.01)
    df = inject_issues(df, "capacity_kg", "negative", 0.01)
    return df


# ---------------------------------------------------------------------------
# 3. ROUTES
# ---------------------------------------------------------------------------
def generate_routes(n=NUM_ROUTES):
    rows = []
    for i in range(n):
        origin, dest = random.sample(MAJOR_CITIES, 2)
        distance = random.randint(50, 900)
        rows.append(
            {
                "route_id": f"RTE-{i+1:04d}",
                "origin_city": origin,
                "destination_city": dest,
                "distance_km": distance,
                "estimated_duration_hrs": round(distance / random.uniform(45, 65), 1),
            }
        )
    df = pd.DataFrame(rows)
    df.attrs["table_name"] = "routes"
    return df


# ---------------------------------------------------------------------------
# 4. TRIPS (vectorized: active vehicles x days, exploded by daily trip count)
# ---------------------------------------------------------------------------
def generate_trips(drivers_df, vehicles_df, routes_df, start, end):
    active_vehicles = vehicles_df.loc[vehicles_df["status"] == "active", "vehicle_id"].to_numpy()
    active_drivers = drivers_df.loc[drivers_df["status"] == "active", "driver_id"].to_numpy()
    route_ids = routes_df["route_id"].to_numpy()
    route_distance = routes_df.set_index("route_id")["distance_km"]

    n_days = (end - start).days
    n_veh = len(active_vehicles)

    trip_counts = rng.choice([0, 1, 2], size=(n_days, n_veh), p=[0.35, 0.45, 0.20])
    total_trips = int(trip_counts.sum())
    print(f"  active vehicles: {n_veh:,} | total trip-slots: {total_trips:,}")

    day_idx, veh_idx = np.nonzero(trip_counts)
    repeats = trip_counts[day_idx, veh_idx]
    day_idx = np.repeat(day_idx, repeats)
    veh_idx = np.repeat(veh_idx, repeats)

    n = len(day_idx)
    vehicle_id_arr = active_vehicles[veh_idx]
    driver_id_arr = rng.choice(active_drivers, size=n)
    route_id_arr = rng.choice(route_ids, size=n)
    base_distance_arr = route_distance.loc[route_id_arr].to_numpy()

    base_dates = np.array([start + timedelta(days=int(d)) for d in range(n_days)])
    day_dates = base_dates[day_idx]
    hour_offsets = rng.integers(4, 21, size=n)
    minute_choices = rng.choice([0, 15, 30, 45], size=n)
    start_times = [
        d.replace(hour=int(h), minute=int(m))
        for d, h, m in zip(day_dates, hour_offsets, minute_choices)
    ]

    speeds = rng.uniform(45, 65, size=n)
    duration_hrs = base_distance_arr / speeds
    end_times = [st + timedelta(hours=float(dur)) for st, dur in zip(start_times, duration_hrs)]
    distance_variance = rng.uniform(0.95, 1.08, size=n)
    distance_km = np.round(base_distance_arr * distance_variance, 1)

    trip_id_arr = [f"TRP-{i+1:08d}" for i in range(n)]
    status_arr = rng.choice(["completed", "cancelled", "in_progress"], size=n, p=[0.90, 0.06, 0.04])

    df = pd.DataFrame(
        {
            "trip_id": trip_id_arr,
            "vehicle_id": vehicle_id_arr,
            "driver_id": driver_id_arr,
            "route_id": route_id_arr,
            "start_time": start_times,
            "end_time": end_times,
            "distance_km": distance_km,
            "status": status_arr,
        }
    )
    df.attrs["table_name"] = "trips"
    df = inject_issues(df, "end_time", "out_of_order", 0.01, other_column="start_time")
    df = inject_issues(df, "vehicle_id", "invalid_fk", 0.005)
    return df


# ---------------------------------------------------------------------------
# 5. DELIVERIES (vectorized: explode trips by random delivery count)
# ---------------------------------------------------------------------------
def generate_deliveries(trips_df, pool_size=3000):
    n_trips = len(trips_df)
    n_deliv_per_trip = rng.choice([1, 2, 3], size=n_trips, p=[0.6, 0.3, 0.1])
    total = int(n_deliv_per_trip.sum())

    trip_idx = np.repeat(np.arange(n_trips), n_deliv_per_trip)
    trip_id_arr = trips_df["trip_id"].to_numpy()[trip_idx]
    trip_start = pd.to_datetime(trips_df["start_time"]).to_numpy()[trip_idx]
    trip_end = pd.to_datetime(trips_df["end_time"]).to_numpy()[trip_idx]

    trip_duration_hrs = (trip_end - trip_start) / np.timedelta64(1, "h")
    trip_duration_hrs = np.clip(trip_duration_hrs, 1, None)
    frac_hours = rng.uniform(0.5, 1.0, size=total) * trip_duration_hrs
    scheduled = trip_start + (frac_hours * np.timedelta64(1, "h")).astype("timedelta64[m]")

    actual_offset_min = rng.integers(-15, 91, size=total)
    actual = scheduled + (actual_offset_min * np.timedelta64(1, "m"))

    # Pre-generate pools of realistic strings once, then sample with
    # replacement — avoids millions of individual Faker calls at this scale.
    company_pool = [fake.company() for _ in range(pool_size)]
    address_pool = [fake.address().replace("\n", ", ") for _ in range(pool_size)]
    phone_pool = [fake.msisdn()[:11] for _ in range(pool_size)]

    df = pd.DataFrame(
        {
            "delivery_id": [f"DLV-{i+1:08d}" for i in range(total)],
            "trip_id": trip_id_arr,
            "customer_name": rng.choice(company_pool, size=total),
            "delivery_address": rng.choice(address_pool, size=total),
            "scheduled_time": scheduled,
            "actual_delivery_time": actual,
            "status": rng.choice(["delivered", "failed", "returned"], size=total, p=[0.92, 0.05, 0.03]),
            "customer_phone": rng.choice(phone_pool, size=total),
        }
    )
    df.attrs["table_name"] = "deliveries"
    df = inject_issues(df, "customer_phone", "null", 0.03)
    df = inject_issues(df, "delivery_id", "duplicate_id", 0.01)
    df = inject_issues(df, "actual_delivery_time", "out_of_order", 0.01, other_column="scheduled_time")
    return df


# ---------------------------------------------------------------------------
# 6. MAINTENANCE EVENTS
# ---------------------------------------------------------------------------
def generate_maintenance_events(vehicles_df, start, end):
    n_veh = len(vehicles_df)
    n_events_per_veh = rng.integers(1, 6, size=n_veh)
    total = int(n_events_per_veh.sum())
    veh_idx = np.repeat(np.arange(n_veh), n_events_per_veh)
    vehicle_id_arr = vehicles_df["vehicle_id"].to_numpy()[veh_idx]

    days_offset = rng.integers(0, (end - start).days, size=total)
    dates = [(start + timedelta(days=int(d))).date() for d in days_offset]

    odometer = np.zeros(total, dtype=int)
    pos = 0
    for count in n_events_per_veh:
        base = rng.integers(10_000, 50_000)
        increments = rng.integers(500, 5000, size=count).cumsum()
        odometer[pos:pos + count] = base + increments
        pos += count

    df = pd.DataFrame(
        {
            "maintenance_id": [f"MNT-{i+1:07d}" for i in range(total)],
            "vehicle_id": vehicle_id_arr,
            "maintenance_date": dates,
            "maintenance_type": rng.choice(["routine", "repair", "inspection"], size=total, p=[0.55, 0.30, 0.15]),
            "cost": np.round(rng.uniform(5_000, 250_000, size=total), 2),
            "odometer_reading": odometer,
        }
    )
    df.attrs["table_name"] = "maintenance_events"
    df = inject_issues(df, "maintenance_date", "null", 0.02)
    df = inject_issues(df, "cost", "negative", 0.015)
    return df


# ---------------------------------------------------------------------------
# 7. OPERATING COSTS (vectorized: trip-linked fuel+toll, plus monthly insurance)
# ---------------------------------------------------------------------------
def generate_operating_costs(trips_df, vehicles_df):
    n_trips = len(trips_df)

    trip_id_2x = np.repeat(trips_df["trip_id"].to_numpy(), 2)
    vehicle_id_2x = np.repeat(trips_df["vehicle_id"].to_numpy(), 2)
    distance_2x = np.repeat(trips_df["distance_km"].to_numpy(), 2)
    start_date_2x = np.repeat(pd.to_datetime(trips_df["start_time"]).dt.date.to_numpy(), 2)
    cost_type_2x = np.tile(["fuel", "toll"], n_trips)

    fuel_mask = cost_type_2x == "fuel"
    amounts = np.empty(len(cost_type_2x))
    amounts[fuel_mask] = np.round(distance_2x[fuel_mask] * rng.uniform(120, 180, size=fuel_mask.sum()), 2)
    amounts[~fuel_mask] = np.round(rng.uniform(500, 5000, size=(~fuel_mask).sum()), 2)

    trip_costs = pd.DataFrame(
        {
            "trip_id": trip_id_2x,
            "vehicle_id": vehicle_id_2x,
            "cost_type": cost_type_2x,
            "amount": amounts,
            "cost_date": start_date_2x,
        }
    )

    n_veh = len(vehicles_df)
    veh_ids_rep = np.repeat(vehicles_df["vehicle_id"].to_numpy(), SIM_MONTHS)
    month_idx = np.tile(np.arange(SIM_MONTHS), n_veh)
    cost_dates = [(SIM_START + timedelta(days=30 * int(m))).date() for m in month_idx]

    insurance_costs = pd.DataFrame(
        {
            "trip_id": [None] * len(veh_ids_rep),
            "vehicle_id": veh_ids_rep,
            "cost_type": "insurance",
            "amount": np.round(rng.uniform(15_000, 40_000, size=len(veh_ids_rep)), 2),
            "cost_date": cost_dates,
        }
    )

    df = pd.concat([trip_costs, insurance_costs], ignore_index=True)
    df.insert(0, "cost_id", [f"CST-{i+1:08d}" for i in range(len(df))])
    df.attrs["table_name"] = "operating_costs"
    df = inject_issues(df, "amount", "negative", 0.01)
    return df


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main(output_dir=None):
    if output_dir is None:
        # default to <project_root>/data, relative to this script's location
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

    os.makedirs(output_dir, exist_ok=True)

    print("Generating drivers...")
    drivers_df = generate_drivers()

    print("Generating vehicles...")
    vehicles_df = generate_vehicles()

    print("Generating routes...")
    routes_df = generate_routes()

    print("Generating trips...")
    trips_df = generate_trips(
        drivers_df,
        vehicles_df,
        routes_df,
        SIM_START,
        SIM_END
    )
    print(f"  -> {len(trips_df):,} trips generated")

    print("Generating deliveries...")
    deliveries_df = generate_deliveries(trips_df)
    print(f"  -> {len(deliveries_df):,} deliveries generated")

    print("Generating maintenance events...")
    maintenance_df = generate_maintenance_events(
        vehicles_df,
        SIM_START,
        SIM_END
    )
    print(f"  -> {len(maintenance_df):,} maintenance events generated")

    print("Generating operating costs...")
    costs_df = generate_operating_costs(trips_df, vehicles_df)
    print(f"  -> {len(costs_df):,} cost records generated")

    tables = {
        "drivers": drivers_df,
        "vehicles": vehicles_df,
        "routes": routes_df,
        "trips": trips_df,
        "deliveries": deliveries_df,
        "maintenance_events": maintenance_df,
        "operating_costs": costs_df,
    }

    for name, df in tables.items():
        path = f"{output_dir}/{name}.csv"
        df.to_csv(path, index=False)
        print(f"Wrote {path} ({len(df):,} rows)")

    dq_log_df = pd.DataFrame(data_quality_log)
    dq_log_df.to_csv(
        f"{output_dir}/data_quality_log.csv",
        index=False
    )
    print(
        f"Wrote {output_dir}/data_quality_log.csv "
        f"({len(dq_log_df)} injection events)"
    )

    return tables


if __name__ == "__main__":
    main()
