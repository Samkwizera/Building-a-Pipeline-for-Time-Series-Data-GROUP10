# Task 2 — Database Design (SQL + MongoDB)

Dataset: [Hourly Energy Consumption](https://www.kaggle.com/datasets/robikscube/hourly-energy-consumption) — AEP_hourly.csv

---

## Folder Structure

```
task2/
├── sql/
│   ├── schema.sql            # CREATE TABLE statements
│   ├── seed_and_queries.sql  # Sample data + 3 queries
│   └── load_data.py          # Bulk loads AEP_hourly.csv into MySQL
├── mongodb/
│   ├── collection_design.js  # Sample documents + 3 queries (run in Compass shell)
│   └── load_data.py          # Bulk loads AEP_hourly.csv into MongoDB
└── docs/
    └── erd.svg               # Entity Relationship Diagram
```

---

## MySQL Setup

### Step 1 — Create the database

Open MySQL Workbench, connect to your local server, then run:

```sql
CREATE DATABASE energy_db;
USE energy_db;
```

### Step 2 — Run the schema

Open `sql/schema.sql` in Workbench and execute it. This creates the 3 tables.

### Step 3 — Load sample data and run queries

Open `sql/seed_and_queries.sql` and execute it. This inserts sample rows and runs all 3 queries.

### Step 4 — Load the full dataset (optional)

Put `AEP_hourly.csv` in the `sql/` folder, then:

```bash
pip install mysql-connector-python pandas
python sql/load_data.py
```

Update the password in `load_data.py` before running.

---

## MongoDB Setup

### Step 1 — Start MongoDB

Make sure MongoDB is running locally (default port 27017).

### Step 2 — Run the collection design

Open MongoDB Compass, click "Open MongoDB Shell" at the bottom, then paste and run `mongodb/collection_design.js` section by section.

### Step 3 — Load the full dataset (optional)

Put `AEP_hourly.csv` in the `mongodb/` folder, then:

```bash
pip install pymongo pandas
python mongodb/load_data.py
```

---

## Schema Overview

### SQL Tables

| Table             | Purpose                                                                 |
| ----------------- | ----------------------------------------------------------------------- |
| `regions`         | Stores each energy region/provider                                      |
| `time_periods`    | Breaks each timestamp into components (year, month, hour, season, etc.) |
| `energy_readings` | Core fact table — one row per hourly reading                            |

### MongoDB Collection

One collection: `energy_readings`
Each document embeds the region, datetime, consumption value, and all time features in a single document for fast reads.

---

## Queries Implemented

| #   | Query                              | SQL                                  | MongoDB                         |
| --- | ---------------------------------- | ------------------------------------ | ------------------------------- |
| 1   | Latest energy reading              | `ORDER BY datetime DESC LIMIT 1`     | `.sort({datetime:-1}).limit(1)` |
| 2   | Readings by date range             | `WHERE datetime BETWEEN ... AND ...` | `$gte / $lte` on datetime       |
| 3   | Average consumption by hour of day | `GROUP BY hour`                      | `$group` aggregation            |
