-- this is for :
-- Seed Data: Insert sample records for testing

-- Insert region
INSERT INTO
    regions (region_name, description)
VALUES (
        'AEP',
        'American Electric Power - covers parts of the Midwest and Appalachia'
    );

-- Insert sample time periods
INSERT INTO
    time_periods (
        datetime,
        year,
        month,
        day,
        hour,
        day_of_week,
        is_weekend,
        season
    )
VALUES (
        '2004-10-01 01:00:00',
        2004,
        10,
        1,
        1,
        4,
        FALSE,
        'Autumn'
    ),
    (
        '2004-10-01 02:00:00',
        2004,
        10,
        1,
        2,
        4,
        FALSE,
        'Autumn'
    ),
    (
        '2004-10-01 03:00:00',
        2004,
        10,
        1,
        3,
        4,
        FALSE,
        'Autumn'
    ),
    (
        '2004-10-01 04:00:00',
        2004,
        10,
        1,
        4,
        4,
        FALSE,
        'Autumn'
    ),
    (
        '2004-10-01 05:00:00',
        2004,
        10,
        1,
        5,
        4,
        FALSE,
        'Autumn'
    ),
    (
        '2004-10-02 01:00:00',
        2004,
        10,
        2,
        1,
        5,
        FALSE,
        'Autumn'
    ),
    (
        '2004-10-02 14:00:00',
        2004,
        10,
        2,
        14,
        5,
        FALSE,
        'Autumn'
    ),
    (
        '2004-10-03 10:00:00',
        2004,
        10,
        3,
        10,
        6,
        TRUE,
        'Autumn'
    ),
    (
        '2005-07-15 15:00:00',
        2005,
        7,
        15,
        15,
        4,
        FALSE,
        'Summer'
    ),
    (
        '2005-07-15 16:00:00',
        2005,
        7,
        15,
        16,
        4,
        FALSE,
        'Summer'
    );

-- Insert sample energy readings (region_id=1 = AEP)
INSERT INTO
    energy_readings (
        region_id,
        period_id,
        consumption_mw
    )
VALUES (1, 1, 13478.0),
    (1, 2, 12865.0),
    (1, 3, 12577.0),
    (1, 4, 12517.0),
    (1, 5, 12670.0),
    (1, 6, 13100.0),
    (1, 7, 15200.0),
    (1, 8, 11900.0),
    (1, 9, 17800.0),
    (1, 10, 18200.0);

-- for this first quesry we just get the latest energy reading
SELECT r.region_name, tp.datetime, er.consumption_mw
FROM
    energy_readings er
    JOIN regions r ON er.region_id = r.region_id
    JOIN time_periods tp ON er.period_id = tp.period_id
ORDER BY tp.datetime DESC
LIMIT 1;

-- Query 2: weget all readings within a date range

SELECT r.region_name, tp.datetime, tp.hour, tp.is_weekend, er.consumption_mw
FROM
    energy_readings er
    JOIN regions r ON er.region_id = r.region_id
    JOIN time_periods tp ON er.period_id = tp.period_id
WHERE
    tp.datetime BETWEEN '2004-10-01 00:00:00' AND '2004-10-03 23:59:59'
ORDER BY tp.datetime ASC;

-- Query 3: Average consumption by hour of day (all time)

SELECT
    tp.hour,
    ROUND(AVG(er.consumption_mw), 2) AS avg_consumption_mw,
    COUNT(*) AS total_readings
FROM
    energy_readings er
    JOIN time_periods tp ON er.period_id = tp.period_id
GROUP BY
    tp.hour
ORDER BY tp.hour ASC;