# Time-Series Pipeline — Hourly Energy Consumption (Group 10)

An end-to-end pipeline for forecasting hourly electricity demand on the PJM grid,
built around the [Hourly Energy Consumption](https://www.kaggle.com/datasets/robikscube/hourly-energy-consumption)
dataset. We forecast **PJME** (PJM East) demand one hour ahead from its own recent
history and calendar features.

## Problem

PJME is a regional load series sampled every hour from 2002 to 2018 (~145k readings).
Grid operators need short-term demand forecasts to schedule generation, so the target
is the next hour's consumption in megawatts (`PJME_MW`). The series has strong daily,
weekly and yearly cycles, which makes it a good fit for lag and moving-average features.

## Repository layout

```
data/raw/            all region CSVs (PJME is the primary series)
src/preprocessing.py reusable pipeline: load, clean, feature-engineer
notebooks/           01 EDA, 02 analytical questions, 03 modeling
models/              trained model saved for the forecast script
outputs/figures/     plots exported for the report
```

## Setup

```bash
pip install -r requirements.txt
jupyter notebook          # then run the notebooks in order
```

## Tasks

- **Task 1 — Preprocessing, analysis & modeling** ✅ (`notebooks/`, `src/preprocessing.py`)
  - `01_eda.ipynb` — time range, granularity, missing values, distributions
  - `02_analysis.ipynb` — analytical questions (trend, seasonality, lag effects, moving averages, external correlation)
  - `03_modeling.ipynb` — model, hyperparameter tuning, experiment comparison
- **Task 2 — SQL + MongoDB design** — I worked with the group on Task 2 of our group assignment where we were required to design and implement two databases out of the Hourly Energy Consumption dataset provided by Kaggle. I made a 3-table relational schema design for MySQL, then drew an ERD, wrote the SQL schema scripts and implemented 3 queries for the latest record, date range filtering, and average consumption by hour. I created a collection for MongoDB that had all the pertinent data associated with a single hourly reading (region, datetime, consumption value, and time breakdown fields), and I wrote those same 3 queries with the MongoDB syntax. Both implementations are structured, documented and suitable to be passed to the teammate working on Task 3, who will develop the API on top of them.
- **Task 3 — CRUD API** — _in progress_
- **Task 4 — Forecast script** — _in progress_ (imports `src/preprocessing.py`)

## Team

| Member | Component |
|--------|-----------|
| Samuel Kwizera Ihimbazwe | Task 1 — preprocessing, EDA, analysis, modeling |
| Kayumba David Pontient | Task 2 — SQL + MongoDB design |
| _teammate_ | Task 3 — CRUD API |
| _teammate_ | Task 4 — forecast script |
