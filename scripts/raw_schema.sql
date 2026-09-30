CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.drivers (
    driver_id text,
    first_name text,
    last_name text,
    phone_number text,
    license_number text,
    license_expiry date,
    hire_date date,
    state_of_origin text,
    status text
);

CREATE TABLE IF NOT EXISTS raw.vehicles (
    vehicle_id text,
    plate_number text,
    vehicle_type text,
    make text,
    model text,
    year integer,
    capacity_kg numeric,
    acquisition_date date,
    status text
);

CREATE TABLE IF NOT EXISTS raw.routes (
    route_id text,
    origin_city text,
    destination_city text,
    distance_km numeric,
    estimated_duration_hrs numeric
);

CREATE TABLE IF NOT EXISTS raw.trips (
    trip_id text,
    vehicle_id text,
    driver_id text,
    route_id text,
    start_time timestamp without time zone,
    end_time timestamp without time zone,
    distance_km numeric,
    status text
);

CREATE TABLE IF NOT EXISTS raw.deliveries (
    delivery_id text,
    trip_id text,
    customer_name text,
    delivery_address text,
    scheduled_time timestamp without time zone,
    actual_delivery_time timestamp without time zone,
    status text,
    customer_phone text
);

CREATE TABLE IF NOT EXISTS raw.maintenance_events (
    maintenance_id text,
    vehicle_id text,
    maintenance_date date,
    maintenance_type text,
    cost numeric,
    odometer_reading numeric
);

CREATE TABLE IF NOT EXISTS raw.operating_costs (
    cost_id text,
    trip_id text,
    vehicle_id text,
    cost_type text,
    amount numeric,
    cost_date date
);
