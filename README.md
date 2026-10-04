# 🌍 Air Quality Analysis using Hadoop MapReduce

A Big Data project for analyzing **India's Air Quality dataset (2015–2020)** using **Apache Hadoop, HDFS, Hadoop Streaming, and Python MapReduce**.

The project processes a large air-quality dataset and performs distributed analysis using two MapReduce jobs:

1. **Average PM2.5 concentration per monitoring station**
2. **AQI category frequency per date**

---

## 📌 Project Overview

Air-quality datasets contain millions of records collected from monitoring stations across India. Processing such datasets using traditional single-machine scripts can become inefficient as the data volume increases.

This project demonstrates how **Hadoop MapReduce** can be used to process and analyze large-scale air-quality data.

### Technologies Used

* **Apache Hadoop 3.3.6**
* **HDFS** — distributed storage
* **Hadoop MapReduce**
* **Hadoop Streaming**
* **Python 3.9**
* **Pandas** — data preprocessing
* **Jupyter Notebook**
* **Git & GitHub**
* **Windows**

---

## 📊 Dataset

**Dataset:** India Air Quality Data (2015–2020)

The original dataset contains air-quality observations collected from monitoring stations across India.

### Important columns

| Column       | Description                                 |
| ------------ | ------------------------------------------- |
| `StationId`  | Unique identifier of the monitoring station |
| `Datetime`   | Date and time of observation                |
| `PM2.5`      | Concentration of fine particulate matter    |
| `AQI_Bucket` | Air Quality Index category                  |

The project uses a cleaned version of the dataset containing approximately **1.88 million records**.

---

# 🏗️ System Architecture

```text
                 Air Quality CSV
                       │
                       ▼
              Data Preprocessing
                       │
                       ▼
                  Cleaned CSV
                       │
                       ▼
                     HDFS
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
       PM2.5 MapReduce      AQI MapReduce
              │                 │
              ▼                 ▼
          Mapper            Mapper
              │                 │
              ▼                 ▼
        Shuffle & Sort     Shuffle & Sort
              │                 │
              ▼                 ▼
          Reducer            Reducer
              │                 │
              ▼                 ▼
     Average PM2.5       AQI Bucket Counts
       per Station           per Date
```

---

# 🔎 MapReduce Jobs

## 1. Average PM2.5 per Station

### Mapper

The mapper reads each air-quality record and emits:

```text
(StationId, PM2.5)
```

Example:

```text
AP001    42.5
AP001    35.0
AP001    38.5
```

### Shuffle and Sort

Hadoop automatically groups records having the same `StationId`.

```text
AP001 → 42.5, 35.0, 38.5
```

### Reducer

The reducer calculates the average:

```text
Average PM2.5 = Sum of PM2.5 values / Number of observations
```

Example output:

```text
AP001    38.67
```

### Output

The final output contains the average PM2.5 concentration for each monitoring station.

---

## 2. AQI Bucket Count per Date

### Mapper

The mapper extracts the date and AQI category:

```text
(Date, AQI_Bucket)
```

Example:

```text
2015-12-02    Poor
2015-12-02    Very Poor
2015-12-02    Poor
2015-12-02    Good
```

### Shuffle and Sort

Hadoop groups records by date.

### Reducer

The reducer counts the occurrences of each AQI category for every date.

Example:

```text
2015-12-02    Poor          61
2015-12-02    Very Poor     97
2015-12-02    Severe        41
2015-12-02    Good          56
```

---

# 📁 Project Structure

```text
AirQualityAnalysis-Big-Data-Project/
│
├── air_quality_cleaned.csv
│
├── dataPreprocessing.ipynb
├── textToCsvConverter.ipynb
│
├── mapper_avg_pm25.py
├── reducer_avg_pm25.py
│
├── mapper_aqi_bucket.py
├── reducer_aqi_bucket.py
│
├── pm25_output.txt
├── aqi_bucket_output.txt
│
├── stations.csv
├── sample_input.csv
├── README.md
└── ...
```

---

# ⚙️ Hadoop Setup

This project was implemented using:

```text
Hadoop 3.3.6
Python 3.9.13
Java 21
Windows
```

HDFS and YARN are used to execute the MapReduce jobs.

---

# 🚀 Running the Project

## 1. Start Hadoop

Start HDFS:

```cmd
start-dfs.cmd
```

Start YARN:

```cmd
start-yarn.cmd
```

Verify HDFS:

```cmd
hdfs dfsadmin -report
```

---

## 2. Upload Dataset to HDFS

Create the HDFS input directory:

```cmd
hdfs dfs -mkdir -p /airquality/input
```

Upload the cleaned dataset:

```cmd
hdfs dfs -put air_quality_cleaned.csv /airquality/input/
```

Verify:

```cmd
hdfs dfs -ls /airquality/input
```

---

# ▶️ Run PM2.5 MapReduce

```cmd
hadoop jar "%HADOOP_HOME%\share\hadoop\tools\lib\hadoop-streaming-3.3.6.jar" -files "mapper_avg_pm25.py,reducer_avg_pm25.py" -input /airquality/input/air_quality_cleaned.csv -output /airquality/output_avg_pm25 -mapper "python mapper_avg_pm25.py" -reducer "python reducer_avg_pm25.py"
```

View the output:

```cmd
hdfs dfs -cat /airquality/output_avg_pm25/part-00000
```

---

# ▶️ Run AQI MapReduce

```cmd
hadoop jar "%HADOOP_HOME%\share\hadoop\tools\lib\hadoop-streaming-3.3.6.jar" -files "mapper_aqi_bucket.py,reducer_aqi_bucket.py" -input /airquality/input/air_quality_cleaned.csv -output /airquality/output_aqi_bucket -mapper "python mapper_aqi_bucket.py" -reducer "python reducer_aqi_bucket.py"
```

View the output:

```cmd
hdfs dfs -cat /airquality/output_aqi_bucket/part-00000
```

---

# 📈 Results

### PM2.5 Analysis

The PM2.5 MapReduce job processed approximately **1.88 million input records** and generated the average PM2.5 concentration for **99 monitoring stations**.

Example:

```text
AP001    38.75
AP005    48.27
AS001    61.61
BR005    71.89
BR006    33.70
```

### AQI Analysis

The AQI MapReduce job processed approximately **1.88 million records** and produced **10,667 date-category results**.

Example:

```text
2015-12-02    Poor          61
2015-12-02    Very Poor     97
2015-12-02    Severe        41
2015-12-02    Good          56
2015-12-02    Moderate      23
2015-12-02    Satisfactory  57
```

---

# 🧠 Why Hadoop MapReduce?

Traditional Python processing runs primarily on a single machine.

Hadoop provides:

* Distributed storage using **HDFS**
* Parallel processing using **MapReduce**
* Automatic **shuffle and sort**
* Fault tolerance
* Scalability for larger datasets

Although Python is used to implement the mapper and reducer, **Hadoop remains responsible for distributing the data and executing the MapReduce workflow**.

Hadoop Streaming makes it possible to use Python programs instead of writing the MapReduce logic entirely in Java.

---

# 🔄 MapReduce Data Flow

### PM2.5

```text
CSV Record
    ↓
Mapper
    ↓
(StationId, PM2.5)
    ↓
Shuffle & Sort
    ↓
StationId → PM2.5 values
    ↓
Reducer
    ↓
Average PM2.5
```

### AQI

```text
CSV Record
    ↓
Mapper
    ↓
(Date, AQI_Bucket)
    ↓
Shuffle & Sort
    ↓
Date → AQI categories
    ↓
Reducer
    ↓
AQI category counts
```

---

# 👩‍💻 Author

**Nida**

Computer Engineering
MCT's Rajiv Gandhi Institute of Technology, Mumbai

---

## ⭐ Key Learning Outcomes

Through this project, the following Big Data concepts were implemented:

* HDFS
* Hadoop ecosystem
* MapReduce programming model
* Hadoop Streaming
* Mapper and Reducer design
* Shuffle and Sort
* Distributed data processing
* Large-scale CSV processing
* Data preprocessing
* Big Data workflow on Windows

---

## 📜 License

This project is intended for **academic and educational purposes**.
