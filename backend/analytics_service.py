from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT_DIR / "air_quality_cleaned.csv"
AQI_OUTPUT_PATH = ROOT_DIR / "output_aqi_bucket.txt"
PM25_OUTPUT_PATH = ROOT_DIR / "output_avg_pm25.txt"


@lru_cache(maxsize=1)
def get_dataset_info() -> dict[str, Any]:
    df = pd.read_csv(DATASET_PATH)
    df["Datetime"] = pd.to_datetime(df["Datetime"], errors="coerce")
    date_min = df["Datetime"].min()
    date_max = df["Datetime"].max()
    geo_summary = get_geography_summary()
    return {
        "name": "India Air Quality Data (2015-2020)",
        "source": "Air-quality monitoring stations across India",
        "time_period": f"{date_min.date()} to {date_max.date()}",
        "records": int(len(df)),
        "columns": df.columns.tolist(),
        "stations": int(df["StationId"].nunique()),
        "days_analyzed": int(df["Datetime"].dt.date.nunique()),
        "missing_values": int(df.isna().sum().sum()),
        "aqi_categories": sorted(df["AQI_Bucket"].dropna().unique().tolist()),
        "preprocessing": [
            "Removed malformed and incomplete rows",
            "Standardized StationId and AQI_Bucket values",
            "Converted Datetime to a consistent timestamp format",
            "Prepared a cleaned CSV for Hadoop HDFS ingestion",
        ],
        "hdfs_location": "/airquality/input/air_quality_cleaned.csv",
        "mapreduce_jobs": [
            "AQI category counts by date",
            "Average PM2.5 by station",
        ],
        "geospatial_status": geo_summary,
    }


@lru_cache(maxsize=1)
def get_geography_summary() -> dict[str, Any]:
    stations_path = ROOT_DIR / "stations.csv"
    geo_columns = {"latitude", "longitude", "lat", "lon", "lng", "long"}
    try:
        station_df = pd.read_csv(stations_path, encoding="utf-8-sig")
    except FileNotFoundError:
        return {
            "has_geographical_coordinates": False,
            "warning": "No station metadata file was found, so no map can be generated without inventing coordinates.",
            "station_count_by_state": [],
        }

    available_columns = [str(column) for column in station_df.columns]
    has_geo = any(column.lower() in geo_columns for column in available_columns)
    dataset_station_ids = set(pd.read_csv(DATASET_PATH, usecols=["StationId"])["StationId"].dropna().astype(str))
    metadata_station_ids = station_df["StationId"].fillna("").astype(str)
    matched_stations = station_df[metadata_station_ids.isin(dataset_station_ids)].drop_duplicates(subset=["StationId"]).copy()
    matched_station_count = int(matched_stations["StationId"].nunique())
    if has_geo:
        state_counts = station_df.iloc[:, 0:0]
        for column in available_columns:
            if column.lower() in {"state", "province", "region"}:
                state_counts = station_df[column].fillna("Unknown").value_counts().reset_index()
                state_counts.columns = ["state", "count"]
                break
        return {
            "has_geographical_coordinates": True,
            "warning": "Geographical coordinates are present; a map could be shown if appropriate data validation passes.",
            "station_count_by_state": [{"state": row["state"], "count": int(row["count"])} for _, row in state_counts.head(10).iterrows()],
            "available_columns": available_columns,
            "matched_station_count": matched_station_count,
        }

    state_counts = matched_stations["State"].fillna("Unknown").value_counts().reset_index()
    state_counts.columns = ["state", "count"]
    return {
        "has_geographical_coordinates": False,
        "warning": "No usable latitude/longitude data is retained in the cleaned dataset or station metadata. A geographical map is intentionally not generated to avoid fabricating coordinates.",
        "station_count_by_state": [{"state": row["state"], "count": int(row["count"])} for _, row in state_counts.head(10).iterrows()],
        "available_columns": available_columns,
        "matched_station_count": matched_station_count,
        "unmapped_dataset_stations": len(dataset_station_ids - set(metadata_station_ids)),
    }


@lru_cache(maxsize=1)
def get_overview() -> dict[str, Any]:
    df = pd.read_csv(DATASET_PATH)
    df["Datetime"] = pd.to_datetime(df["Datetime"], errors="coerce")
    pm25_values = pd.to_numeric(df["PM2.5"], errors="coerce").dropna()
    aqi_counts = df["AQI_Bucket"].dropna().value_counts()
    pm25_by_station = pd.read_csv(PM25_OUTPUT_PATH, sep="\t", names=["StationId", "Average_PM25"], engine="python")
    pm25_by_station["Average_PM25"] = pd.to_numeric(pm25_by_station["Average_PM25"], errors="coerce")
    most_polluted = pm25_by_station.sort_values("Average_PM25", ascending=False).head(1)
    most_common_aqi = aqi_counts.idxmax() if not aqi_counts.empty else None
    overview = {
        "total_observations": int(len(df)),
        "number_of_stations": int(df["StationId"].nunique()),
        "average_pm25": round(float(pm25_values.mean()), 2),
        "maximum_pm25": round(float(pm25_values.max()), 2),
        "minimum_pm25": round(float(pm25_values.min()), 2),
        "most_common_aqi_category": most_common_aqi,
        "most_polluted_station": {
            "station_id": most_polluted.iloc[0]["StationId"].strip() if not most_polluted.empty else None,
            "average_pm25": round(float(most_polluted.iloc[0]["Average_PM25"]), 2) if not most_polluted.empty else None,
        },
        "days_analyzed": int(df["Datetime"].dt.date.nunique()),
        "aqi_category_distribution": [{"category": str(key), "count": int(value)} for key, value in aqi_counts.items()],
        "total_stations_with_avg_pm25": int(len(pm25_by_station)),
    }
    return overview


@lru_cache(maxsize=1)
def get_aqi_by_date() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with AQI_OUTPUT_PATH.open("r", encoding="utf-8", errors="replace") as infile:
        for raw_line in infile:
            line = raw_line.strip()
            if not line:
                continue
            parts = [part.strip() for part in line.split("\t")]
            if len(parts) >= 3:
                rows.append({"date": parts[0], "aqi_bucket": parts[1], "count": int(parts[2])})
    return rows


@lru_cache(maxsize=1)
def get_pm25_by_station() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with PM25_OUTPUT_PATH.open("r", encoding="utf-8", errors="replace") as infile:
        for raw_line in infile:
            line = raw_line.strip()
            if not line:
                continue
            parts = [part.strip() for part in line.split("\t")]
            if len(parts) >= 2:
                station = parts[0]
                value = parts[1]
                try:
                    value_float = float(value)
                except ValueError:
                    continue
                rows.append({"station_id": station, "average_pm25": value_float})
    return rows


@lru_cache(maxsize=1)
def get_station_details() -> list[dict[str, Any]]:
    pm25 = pd.DataFrame(get_pm25_by_station())
    if pm25.empty:
        return []
    pm25["average_pm25"] = pd.to_numeric(pm25["average_pm25"], errors="coerce")
    return [
        {
            "station_id": row["station_id"],
            "average_pm25": round(float(row["average_pm25"]), 2),
        }
        for _, row in pm25.sort_values("average_pm25", ascending=False).iterrows()
    ]


@lru_cache(maxsize=1)
def get_jobs_metadata() -> dict[str, Any]:
    dataset_info = get_dataset_info()
    aqi_rows = get_aqi_by_date()
    pm25_rows = get_pm25_by_station()
    return {
        "job_1": {
            "name": "AQI Category Analysis",
            "status": "Completed",
            "input_records": dataset_info["records"],
            "output_records": len(aqi_rows),
            "operation": "COUNT by date and AQI bucket",
            "hadoop_output": str(AQI_OUTPUT_PATH.name),
        },
        "job_2": {
            "name": "Average PM2.5 Analysis",
            "status": "Completed",
            "input_records": dataset_info["records"],
            "output_records": len(pm25_rows),
            "operation": "AVG(PM2.5) by station",
            "hadoop_output": str(PM25_OUTPUT_PATH.name),
        },
    }


def get_aqi_trend(limit: int = 30) -> list[dict[str, Any]]:
    rows = get_aqi_by_date()
    trend: dict[str, dict[str, int]] = {}
    for row in rows:
        day = row["date"]
        if day not in trend:
            trend[day] = {}
        trend[day][row["aqi_bucket"]] = row["count"]
    ordered_days = list(trend.keys())[-limit:]
    data = []
    for day in ordered_days:
        payload = {"date": day}
        for key, value in trend[day].items():
            payload[key] = value
        data.append(payload)
    return data


def get_data(page: int = 1, page_size: int = 50, station: str | None = None, aqi_bucket: str | None = None, date_from: str | None = None, date_to: str | None = None, pm25_min: float | None = None, pm25_max: float | None = None) -> dict[str, Any]:
    df = pd.read_csv(DATASET_PATH)
    df["Datetime"] = pd.to_datetime(df["Datetime"], errors="coerce")
    if station:
        df = df[df["StationId"].astype(str).str.lower() == station.lower()]
    if aqi_bucket:
        df = df[df["AQI_Bucket"].astype(str).str.lower() == aqi_bucket.lower()]
    if date_from:
        df = df[df["Datetime"] >= pd.to_datetime(date_from)]
    if date_to:
        df = df[df["Datetime"] <= pd.to_datetime(date_to)]
    if pm25_min is not None:
        df = df[pd.to_numeric(df["PM2.5"], errors="coerce") >= float(pm25_min)]
    if pm25_max is not None:
        df = df[pd.to_numeric(df["PM2.5"], errors="coerce") <= float(pm25_max)]

    total = len(df)
    page = max(1, page)
    page_size = max(1, page_size)
    total_pages = max(1, (total + page_size - 1) // page_size) if total else 1
    page = min(page, total_pages)
    start = (page - 1) * page_size
    end = start + page_size
    table = df.iloc[start:end].copy()
    table["Datetime"] = table["Datetime"].dt.strftime("%Y-%m-%d %H:%M:%S") if not table.empty else []
    payload = table.to_dict(orient="records")
    for row in payload:
        if row.get("PM2.5") is not None:
            row["PM2.5"] = round(float(row["PM2.5"]), 2)
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "items": payload,
    }


def get_live_monitoring() -> dict[str, Any]:
    stations = get_station_details()
    above_threshold = sum(1 for item in stations if item["average_pm25"] > 100)
    return {
        "mode": "historical_hadoop_output",
        "stations_analyzed": len(stations),
        "highest_station": stations[0] if stations else None,
        "pm25_threshold": 100,
        "stations_above_threshold": above_threshold,
        "top_stations": stations[:5],
    }
