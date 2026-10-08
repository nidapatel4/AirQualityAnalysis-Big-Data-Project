# Air Quality Big Data Analytics Platform

## Project Title
Air Quality Big Data Analytics Platform

## Problem Statement
Air-quality data is collected at high frequency from many monitoring stations across India. A single-machine approach becomes inefficient when the dataset grows to millions of records. This project demonstrates how Hadoop MapReduce can process the cleaned dataset in a distributed manner, produce aggregated analytics, and expose the results through a backend API and interactive dashboard.

## Objectives
- Preserve the existing Hadoop MapReduce implementation as the project core.
- Validate preprocessing and cleaned data quality.
- Demonstrate HDFS and streaming-based MapReduce processing.
- Produce AQI category counts by date and average PM2.5 per station.
- Expose results through a backend API.
- Present interactive dashboard visuals for dashboard evaluation.
- Document the pipeline for academic reporting.

## Technologies Used
- Python
- Pandas
- Apache Hadoop / HDFS
- Hadoop Streaming
- MapReduce
- Flask
- HTML / CSS / JavaScript
- Chart.js

## Dataset
This project uses the cleaned India air quality dataset prepared from the original raw source. The cleaned file is: `air_quality_cleaned.csv`.

Actual values from the project:
- Records: 1,880,106
- Stations: 107
- Days analyzed: 2,009
- Columns: StationId, Datetime, PM2.5, AQI_Bucket
- Time period: 2015-01-01 to 2020-07-01
- Missing values: actual count is computed at runtime
- PM2.5 range: 0.01 to 1000.0

### Geographic data check
The cleaned dataset does not retain usable latitude/longitude coordinates. The station metadata file includes `StationName`, `City`, and `State`, but no latitude or longitude fields. For this reason, the dashboard does not fabricate a map. It instead reports station coverage by state as a truthful geographic summary.

## Architecture
```text
Raw Dataset
    ↓
Python / Pandas preprocessing
    ↓
Clean CSV
    ↓
HDFS
    ↓
MapReduce job 1: AQI by date/category
    ↓
MapReduce job 2: Average PM2.5 by station
    ↓
Hadoop output files
    ↓
Flask API
    ↓
Interactive dashboard
```

## Hadoop and MapReduce Jobs

### Job 1: AQI Category Analysis
Mapper output format:
```text
(date, AQI_Bucket) -> 1
```
Reducer behavior:
```text
COUNT observations for each (date, AQI_Bucket)
```
Output file:
```text
output_aqi_bucket.txt
```
Example:
```text
2015-01-01	Severe	8
2015-01-01	Very Poor	8
2015-01-02	Very Poor	16
```

### Job 2: Average PM2.5 by Station
Mapper output format:
```text
(StationId, PM2.5)
```
Reducer behavior:
```text
AVG(PM2.5) by StationId
```
Output file:
```text
output_avg_pm25.txt
```
Example:
```text
AP001 	38.75
AP005 	48.27
AS001 	61.61
```

## Hadoop Concepts Demonstrated
- HDFS storage
- Distributed input data
- Mapper logic
- Shuffle and Sort
- Reducer logic
- Aggregation with count and average
- Hadoop output files consumed by backend services

## Project Structure
```text
AirQualityAnalysis-Big-Data-Project/
├── air_quality_cleaned.csv
├── output_aqi_bucket.txt
├── output_avg_pm25.txt
├── mapper_aqi_bucket.py
├── mapper_avg_pm25.py
├── reducer_aqi_bucket.py
├── reducer_avg_pm25.py
├── backend/
│   ├── __init__.py
│   ├── analytics_service.py
│   └── main.py
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── docs/
│   └── project_docs.md
├── tests/
│   └── test_backend.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Dashboard Pages
- Overview Dashboard
- Combined AQI & PM2.5 Analysis
- Geography (state-level station coverage; no fabricated coordinates)
- Historical Monitoring Snapshot (derived from station-average Hadoop output, not live data)
- Big Data Pipeline
- Dataset Information
- About

## Backend API Endpoints
- GET /api/overview
- GET /api/aqi
- GET /api/aqi/trend
- GET /api/pm25
- GET /api/pm25/top-stations
- GET /api/stations
- GET /api/data
- GET /api/dataset-info
- GET /api/jobs
- GET /api/live-monitoring

## How to Run
### 1. Install dependencies
```powershell
cd C:\Users\Amaan\Downloads\AirQualityAnalysis-Big-Data-Project
python -m pip install -r requirements.txt
```

### 2. Start the backend dashboard
```powershell
cd C:\Users\Amaan\Downloads\AirQualityAnalysis-Big-Data-Project
python backend/main.py
```

Open the application in a browser:
```text
http://127.0.0.1:5000/
```

### 3. Optional: Hadoop execution
If Hadoop is installed locally, the original MapReduce commands can be run in a Hadoop environment using the existing mapper and reducer scripts:

```cmd
hadoop jar "%HADOOP_HOME%\share\hadoop\tools\lib\hadoop-streaming-3.3.6.jar" -files "mapper_avg_pm25.py,reducer_avg_pm25.py" -input /airquality/input/air_quality_cleaned.csv -output /airquality/output_avg_pm25 -mapper "python mapper_avg_pm25.py" -reducer "python reducer_avg_pm25.py"
```

```cmd
hadoop jar "%HADOOP_HOME%\share\hadoop\tools\lib\hadoop-streaming-3.3.6.jar" -files "mapper_aqi_bucket.py,reducer_aqi_bucket.py" -input /airquality/input/air_quality_cleaned.csv -output /airquality/output_aqi_bucket -mapper "python mapper_aqi_bucket.py" -reducer "python reducer_aqi_bucket.py"
```

## Validation
The project was validated with unit tests and actual data inspection:
- 6 backend API tests passed
- Full dataset size verified as 1,880,106 records
- AQI output file contains 10,667 date-category rows
- PM2.5 output file contains 107 station averages

## Documentation
The detailed project documentation is available in:
- `docs/project_docs.md`

It includes the architecture diagram, data flow diagram, use case flow, activity flow, sequence flow, and MapReduce workflow diagram.

## Current Limitation
This repository preserves the Hadoop core and exposes the output via a lightweight Flask dashboard. A full Hadoop cluster was not configured in this environment, so the dashboard loads processed Hadoop outputs rather than triggering live cluster execution at every request.

## Viva Guidance
Focus on the story:
- raw dataset
- preprocessing
- HDFS input
- Hadoop streaming mappers and reducers
- shuffle and sort
- aggregated outputs
- Flask API
- interactive dashboard

This is the core academic Big Data pipeline for the project.
