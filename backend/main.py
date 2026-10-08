from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flask import Flask, jsonify, request, send_from_directory

from backend.analytics_service import (
    get_aqi_by_date,
    get_aqi_trend,
    get_dataset_info,
    get_data,
    get_geography_summary,
    get_jobs_metadata,
    get_live_monitoring,
    get_overview,
    get_pm25_by_station,
    get_station_details,
)

BASE_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = BASE_DIR / "frontend"

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/overview")
def api_overview():
    return jsonify(get_overview())


@app.route("/api/aqi")
def api_aqi():
    return jsonify(get_aqi_by_date())


@app.route("/api/aqi/trend")
def api_aqi_trend():
    limit = request.args.get("limit", default=30, type=int)
    return jsonify(get_aqi_trend(limit=limit))


@app.route("/api/pm25")
def api_pm25():
    return jsonify(get_pm25_by_station())


@app.route("/api/pm25/top-stations")
def api_top_stations():
    rows = get_station_details()
    return jsonify(rows[:10])


@app.route("/api/stations")
def api_stations():
    return jsonify(get_station_details())


@app.route("/api/data")
def api_data():
    page = request.args.get("page", default=1, type=int)
    page_size = request.args.get("page_size", default=50, type=int)
    station = request.args.get("station")
    aqi_bucket = request.args.get("aqi_bucket")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    pm25_min = request.args.get("pm25_min", type=float)
    pm25_max = request.args.get("pm25_max", type=float)
    return jsonify(
        get_data(
            page=page,
            page_size=page_size,
            station=station,
            aqi_bucket=aqi_bucket,
            date_from=date_from,
            date_to=date_to,
            pm25_min=pm25_min,
            pm25_max=pm25_max,
        )
    )


@app.route("/api/dataset-info")
def api_dataset_info():
    return jsonify(get_dataset_info())


@app.route("/api/jobs")
def api_jobs():
    return jsonify(get_jobs_metadata())


@app.route("/api/geography")
def api_geography():
    return jsonify(get_geography_summary())


@app.route("/api/live-monitoring")
def api_live_monitoring():
    return jsonify(get_live_monitoring())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
