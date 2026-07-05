# Raw data

Source: [Hourly Energy Consumption](https://www.kaggle.com/datasets/robikscube/hourly-energy-consumption) (PJM Interconnection, via Kaggle).

Each `*_hourly.csv` is one PJM region with two columns: `Datetime` and `<REGION>_MW`
(megawatts consumed that hour). `pjm_hourly_est.csv` is every region joined on the
timestamp.

Task 1 uses **PJME_hourly.csv** as the primary series (target `PJME_MW`, hourly,
2002–2018). **PJMW** covers the same span and is used as an external variable.
