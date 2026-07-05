// Task 2: MongoDB Collection Design
// Dataset used: Hourly Energy Consumption (AEP_hourly.csv)

// for this simply run these in MongoDB Compass > Open MongoDB Shellor paste into mongosh in your terminal


// --- Switch to (or create) our database ---
use energy_db


// ============================================================
// Collection: energy_readings
// Each document = one hourly reading for one region
// ============================================================

// Sample documents showing the structure
db.energy_readings.insertMany([
  {
    region: "AEP",
    datetime: ISODate("2004-10-01T01:00:00Z"),
    consumption_mw: 13478.0,
    time_features: {
      year:        2004,
      month:       10,
      day:         1,
      hour:        1,
      day_of_week: 4,
      is_weekend:  false,
      season:      "Autumn"
    }
  },
  {
    region: "AEP",
    datetime: ISODate("2004-10-01T02:00:00Z"),
    consumption_mw: 12865.0,
    time_features: {
      year:        2004,
      month:       10,
      day:         1,
      hour:        2,
      day_of_week: 4,
      is_weekend:  false,
      season:      "Autumn"
    }
  },
  {
    region: "AEP",
    datetime: ISODate("2004-10-01T03:00:00Z"),
    consumption_mw: 12577.0,
    time_features: {
      year:        2004,
      month:       10,
      day:         1,
      hour:        3,
      day_of_week: 4,
      is_weekend:  false,
      season:      "Autumn"
    }
  },
  {
    region: "AEP",
    datetime: ISODate("2005-07-15T15:00:00Z"),
    consumption_mw: 17800.0,
    time_features: {
      year:        2005,
      month:       7,
      day:         15,
      hour:        15,
      day_of_week: 4,
      is_weekend:  false,
      season:      "Summer"
    }
  },
  {
    region: "AEP",
    datetime: ISODate("2005-07-15T16:00:00Z"),
    consumption_mw: 18200.0,
    time_features: {
      year:        2005,
      month:       7,
      day:         15,
      hour:        16,
      day_of_week: 4,
      is_weekend:  false,
      season:      "Summer"
    }
  }
])


// Create an index on datetime for fast range queries
db.energy_readings.createIndex({ datetime: 1 })
db.energy_readings.createIndex({ region: 1 })



// the first query: weGet the latest energy reading

db.energy_readings.find().sort({ datetime: -1 }).limit(1)



// the second query : Get all readings within a date range

db.energy_readings.find({
  datetime: {
    $gte: ISODate("2004-10-01T00:00:00Z"),
    $lte: ISODate("2004-10-01T23:59:59Z")
  }
}).sort({ datetime: 1 })



// the third query: Average consumption grouped by hour of day

db.energy_readings.aggregate([
  {
    $group: {
      _id:               "$time_features.hour",
      avg_consumption_mw: { $avg: "$consumption_mw" },
      total_readings:     { $sum: 1 }
    }
  },
  { $sort: { _id: 1 } },
  {
    $project: {
      hour:               "$_id",
      avg_consumption_mw: { $round: ["$avg_consumption_mw", 2] },
      total_readings:     1,
      _id:                0
    }
  }
])
