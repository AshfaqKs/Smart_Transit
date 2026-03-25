-- SmartTransit Database Schema
-- Run with: psql -U postgres -d smarttransit_db -f schema.sql

CREATE TABLE IF NOT EXISTS admins (
    admin_id     SERIAL PRIMARY KEY,
    name         VARCHAR(120) NOT NULL,
    email        VARCHAR(200) UNIQUE NOT NULL,
    password     VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    created_at   TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    user_id      SERIAL PRIMARY KEY,
    name         VARCHAR(120) NOT NULL,
    email        VARCHAR(200) UNIQUE NOT NULL,
    password     VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    address      VARCHAR(300),
    created_at   TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bus_drivers (
    driver_id       SERIAL PRIMARY KEY,
    name            VARCHAR(120) NOT NULL,
    email           VARCHAR(200) UNIQUE NOT NULL,
    password        VARCHAR(255) NOT NULL,
    phone_number    VARCHAR(20),
    license_number  VARCHAR(50) UNIQUE NOT NULL,
    approval_status BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS routes (
    route_id    SERIAL PRIMARY KEY,
    route_name  VARCHAR(150) NOT NULL,
    start_point VARCHAR(200) NOT NULL,
    end_point   VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS route_points (
    stop_id     SERIAL PRIMARY KEY,
    route_id    INTEGER NOT NULL REFERENCES routes(route_id) ON DELETE CASCADE,
    stop_name   VARCHAR(100) NOT NULL,
    stop_order  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS buses (
    bus_id           SERIAL PRIMARY KEY,
    bus_number       VARCHAR(30) UNIQUE NOT NULL,
    route_id         INTEGER REFERENCES routes(route_id) ON DELETE SET NULL,
    driver_id        INTEGER REFERENCES bus_drivers(driver_id) ON DELETE SET NULL,
    current_location VARCHAR(300),
    status           VARCHAR(50) DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS police_stations (
    police_id      SERIAL PRIMARY KEY,
    station_name   VARCHAR(200) NOT NULL,
    location       VARCHAR(300),
    contact_number VARCHAR(20),
    email          VARCHAR(200) UNIQUE NOT NULL,
    password       VARCHAR(255) NOT NULL,
    created_at     TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS criminals (
    criminal_id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name        VARCHAR(150) NOT NULL,
    crime_type  VARCHAR(100),
    description TEXT,
    photo       VARCHAR(300),
    police_id   INTEGER REFERENCES police_stations(police_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS missing_persons (
    missing_id  INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name        VARCHAR(150) NOT NULL,
    age         INTEGER,
    description TEXT,
    photo       VARCHAR(300),
    police_id   INTEGER REFERENCES police_stations(police_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS complaints (
    complaint_id              SERIAL PRIMARY KEY,
    user_id                   INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    bus_id                    INTEGER REFERENCES buses(bus_id) ON DELETE SET NULL,
    police_id                 INTEGER REFERENCES police_stations(police_id) ON DELETE SET NULL,
    complaint_type            VARCHAR(100),
    description               TEXT,
    bus_registration          VARCHAR(50),
    bus_location_at_complaint VARCHAR(255),
    photo                     VARCHAR(255),
    status                    VARCHAR(50) DEFAULT 'pending',
    reply                     TEXT,
    created_at                TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reviews (
    review_id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id   INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    bus_id    INTEGER NOT NULL REFERENCES buses(bus_id) ON DELETE CASCADE,
    rating    INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comments  TEXT
);

CREATE TABLE IF NOT EXISTS app_reviews (
    app_review_id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id       INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    rating        INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comments      TEXT,
    created_at    TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS camera_detections (
    detection_id         SERIAL PRIMARY KEY,
    bus_id               INTEGER REFERENCES buses(bus_id) ON DELETE SET NULL,
    detected_person_type VARCHAR(50),
    reference_id         INTEGER,
    detection_time       TIMESTAMP DEFAULT NOW(),
    location             VARCHAR(255),
    alert_status         VARCHAR(50) DEFAULT 'unresolved'
);
