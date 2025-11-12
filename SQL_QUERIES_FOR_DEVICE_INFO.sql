-- Device Info SQL Queries for InfluxDB Cloud Serverless
-- Storage Engine Version 3 uses SQL syntax

-- ============================================
-- Query 1: Get Device by Serial Number
-- ============================================
SELECT "Sr_No",
       "Owner",
       "Date_Of_Register",
       "Device_Name",
       time
FROM "Device_info"
WHERE "Sr_No" = 'DF5647'
  AND time > now() - interval '1 year'
ORDER BY time DESC
LIMIT 1;

-- ============================================
-- Query 2: Check if Serial Number Exists
-- ============================================
SELECT COUNT(*) as count
FROM "Device_info"
WHERE "Sr_No" = 'DF5647'
  AND time > now() - interval '1 year';

-- ============================================
-- Query 3: List All Devices
-- ============================================
SELECT DISTINCT "Sr_No",
       "Owner",
       "Date_Of_Register",
       "Device_Name"
FROM "Device_info"
WHERE time > now() - interval '1 year'
ORDER BY "Sr_No";

-- ============================================
-- Query 4: Count Total Registered Devices
-- ============================================
SELECT COUNT(DISTINCT "Sr_No") as total_devices
FROM "Device_info"
WHERE time > now() - interval '1 year';

-- ============================================
-- Query 5: Get Unassigned Devices
-- ============================================
SELECT "Sr_No",
       "Owner",
       "Date_Of_Register",
       "Device_Name",
       time
FROM "Device_info"
WHERE "Owner" = 'Unassigned'
  AND time > now() - interval '1 year'
ORDER BY time DESC;

-- ============================================
-- Query 6: Get Devices Registered Today
-- ============================================
SELECT "Sr_No",
       "Owner",
       "Date_Of_Register",
       "Device_Name",
       time
FROM "Device_info"
WHERE "Date_Of_Register" = CURRENT_DATE
  AND time > now() - interval '1 year'
ORDER BY time DESC;

-- ============================================
-- Query 7: Get Devices by Date Range
-- ============================================
SELECT "Sr_No",
       "Owner",
       "Date_Of_Register",
       "Device_Name",
       time
FROM "Device_info"
WHERE "Date_Of_Register" >= '2024-01-01'
  AND "Date_Of_Register" <= '2024-01-31'
  AND time > now() - interval '1 year'
ORDER BY time DESC;

-- ============================================
-- Query 8: Get Latest Device Info for All Devices
-- ============================================
SELECT DISTINCT ON ("Sr_No")
       "Sr_No",
       "Owner",
       "Date_Of_Register",
       "Device_Name",
       time
FROM "Device_info"
WHERE time > now() - interval '1 year'
ORDER BY "Sr_No", time DESC;

-- ============================================
-- Query 9: Get Devices by Owner
-- ============================================
SELECT "Sr_No",
       "Owner",
       "Date_Of_Register",
       "Device_Name",
       time
FROM "Device_info"
WHERE "Owner" = 'John Doe'
  AND time > now() - interval '1 year'
ORDER BY time DESC;

-- ============================================
-- Query 10: Get Device Registration Statistics
-- ============================================
SELECT "Date_Of_Register",
       COUNT(DISTINCT "Sr_No") as devices_registered
FROM "Device_info"
WHERE time > now() - interval '1 year'
GROUP BY "Date_Of_Register"
ORDER BY "Date_Of_Register" DESC;

