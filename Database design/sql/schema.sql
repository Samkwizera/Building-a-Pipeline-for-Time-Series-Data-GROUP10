-- Task 2: Relational Database Schema  (first create a database called energy_db)

USE energy_db;
-- Drop tables if they already exist (clean slate for testing)
DROP TABLE IF EXISTS energy_readings;

DROP TABLE IF EXISTS time_periods;

DROP TABLE IF EXISTS regions;

-- Table 1: regions
-- Stores each energy region/provider

CREATE TABLE regions (
    region_id INT AUTO_INCREMENT PRIMARY KEY,
    region_name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255)
);

-- Table 2: time_periods
-- Breaks down each timestamp into components for easy querying

CREATE TABLE time_periods (
    period_id INT AUTO_INCREMENT PRIMARY KEY,
    datetime DATETIME NOT NULL UNIQUE,
    year SMALLINT NOT NULL,
    month TINYINT NOT NULL,
    day TINYINT NOT NULL,
    hour TINYINT NOT NULL,
    day_of_week TINYINT NOT NULL, -- 0=Monday, 6=Sunday
    is_weekend BOOLEAN NOT NULL,
    season VARCHAR(10) NOT NULL -- Spring, Summer, Autumn, Winter
);

-- Table 3: energy_readings
-- Core fact table storing megawatt readings per region per hour

CREATE TABLE energy_readings (
    reading_id INT AUTO_INCREMENT PRIMARY KEY,
    region_id INT NOT NULL,
    period_id INT NOT NULL,
    consumption_mw FLOAT NOT NULL,
    FOREIGN KEY (region_id) REFERENCES regions (region_id),
    FOREIGN KEY (period_id) REFERENCES time_periods (period_id)
);

-- Indexes for faster querying by date and region
CREATE INDEX idx_readings_region ON energy_readings (region_id);

CREATE INDEX idx_readings_period ON energy_readings (period_id);

CREATE INDEX idx_period_datetime ON time_periods (datetime);

CREATE INDEX idx_period_year_month ON time_periods (year, month);