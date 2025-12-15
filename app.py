from flask import Flask, render_template, jsonify, request, session
import json, os
import requests
from dotenv import load_dotenv
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.secret_key = "dev-secret-key"  # REQUIRED for sessions

## Load data
df = pd.read_csv("static/data/modis_2001-2010.csv")
# df = pd.read_csv("static/data/fire1.csv")
# Load API key and base URL from .env
API_KEY = os.getenv("OWM_API_KEY")
BASE_URL = os.getenv("OWM_BASE_URL")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/fire_hotspots")
def fire_hotspots():
    fp = os.path.join(app.root_path, "data", "fire_hotspot.geojson")
    with open(fp) as f:
        data = json.load(f)
    return jsonify(data)


# Admin1 boundary route
@app.route("/api/admin1")
def admin1_boundary():
    fp = os.path.join(app.root_path, "static", "data", "zim_admin1.geojson")
    with open(fp) as f:
        data = json.load(f)
    return jsonify(data)


@app.route("/coordinates-settings")
def coordinates_settings():
    return render_template("coordinates_settings.html")


# Get weather data based on coordinates
# local page to get FWI for 1 point
@app.route("/fwi/form")
def fwi_form():
    return render_template("fwi/fwi_form.html")


@app.route("/fwi/map")
def fwi_map():
    return render_template("fwi/fwi_map.html")


@app.route("/fwi/place", methods=["GET"])
def fwi_place_page():
    """Render the place search page"""
    return render_template("fwi/fwi_place.html")


@app.route("/fwi/place", methods=["POST"])
def fwi_place():
    place = request.form.get("place")

    # Example dictionary — replace with database or full list
    zimbabwe_coords = {
        "Harare": (-17.8292, 31.0522),
        "Bulawayo": (-20.1325, 28.6265),
        "Mutare": (-18.9707, 32.6709),
        "Gweru": (-19.4500, 29.8167),
        "Masvingo": (-20.0637, 30.8277),
        "Kwekwe": (-18.9281, 29.8140),
        "Chinhoyi": (-17.3667, 30.2000),
        "Bindura": (-17.3000, 31.3333),
        "Victoria Falls": (-17.9244, 25.8567),
        "Kariba": (-16.5167, 28.8000),
        "Kadoma": (-18.3333, 29.9167),
        "Marondera": (-18.1853, 31.5519),
    }

    if place not in zimbabwe_coords:
        return jsonify({"error": "Unknown place"}), 400

    lat, lon = zimbabwe_coords[place]

    # Call your weather API
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}"

    response = requests.get(url)

    return jsonify(response.json())


# ---------------- Analytics ----------------#
# ------ Historical fire data and stats------
@app.route("/analytics")
def analytics_hist():
    return render_template("analytics/analytics_hist.html")


# Fire trends
@app.route("/analytics/fires-per-year")
def fires_per_year_page():
    return render_template("analytics/fires_per_year.html")


# Fire trends
@app.route("/analytics/fires-per-year-province")
def fires_per_year_page_provice():
    return render_template("analytics/fires_per_year_province.html")


# Frp trends
@app.route("/analytics/frp-trend")
def frp_trend_page():
    return render_template("analytics/frp_trend.html")


# Frp trends
@app.route("/analytics/yearly-prov-chropleth")
def yearly_prov_chropleth():
    return render_template("analytics/yearly_prov_chropleth.html")


# Historical fire data and stats
# @app.route("/fire")
# def fire_data():
#     # Read CSV data using pandas
#     df = pd.read_csv("static/data/fire.csv")

#     # Calculate simple statistics
#     total_detections = len(df)
#     avg_frp = df["frp"].mean()

#     # Get all data for table
#     fire_data = df.to_dict("records")

#     return render_template(
#         "analytics/analytics_hist.html",
#         total_detections=total_detections,
#         avg_frp=avg_frp,
#         fire_data=fire_data,
#     )


# ------- Make data available to all pages--------
# --- Use decorator
df_cur = pd.read_csv("static/data/fire1.csv")


@app.context_processor
def inject_fire_data():
    total_detections = len(df_cur)
    avg_frp = df_cur["frp"].mean()
    fire_data = df_cur.to_dict("records")
    return dict(total_detections=total_detections, avg_frp=avg_frp, fire_data=fire_data)


# display results external pages
@app.route("/getfwi_1point_ext")
def weather_ext():
    return render_template("getfwi_1point_ext.html")


@app.route("/coordinates_settings_map")
def coordinates_settings_map():
    return render_template("coordinates_settings_map.html")


@app.route("/a")
def a():
    return render_template("a.html")


@app.route("/b")
def b():
    return render_template("b.html")


@app.route("/get_weather", methods=["POST"])
def get_weather():
    lat = request.form.get("lat")
    lon = request.form.get("lon")

    if not lat or not lon:
        return jsonify({"error": "Missing coordinates"}), 400

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}"

    data = requests.get(url).json()
    return jsonify(data)


# ---------Leaflet map settings ---
# -------- Inject Leaflet settings into all templates --------#
@app.context_processor
def leaflet_defaults():
    return {
        "map_center": (-12, 28),
        "map_zoom": 5,
        "tile_url": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        "geojson_url": "/static/data/zim_admin1.geojson",  # absolute path recommended
        "map_style": "height:500px;width:80%;margin:auto;border-radius:8px;",
    }


# ====================FIRE API ENDPOINTS ====================
# ====================FIRE API ENDPOINTS ====================
# fn to add prov name on fire location
def build_df_prov(df):
    import geopandas as gpd
    from shapely.geometry import Point

    # Copy – NEVER mutate df
    df_work = df.copy()

    # Parse date + year (safe)
    df_work["acq_date"] = pd.to_datetime(df_work["acq_date"])
    df_work["year"] = df_work["acq_date"].dt.year

    # Build GeoDataFrame
    gdf = gpd.GeoDataFrame(
        df_work,
        geometry=gpd.points_from_xy(df_work["longitude"], df_work["latitude"]),
        crs="EPSG:4326",
    )

    # Load provinces
    prov = gpd.read_file("static/data/zim_admin1.geojson")
    prov = prov[["ADM1_EN", "geometry"]]

    # Spatial join
    gdf = gpd.sjoin(gdf, prov, how="left", predicate="within")

    # Rename + cleanup
    gdf = gdf.rename(columns={"ADM1_EN": "province"})
    gdf = gdf.drop(columns=["index_right", "geometry"])

    return pd.DataFrame(gdf)


# Run the fn to create the ne gdf
df_prov = build_df_prov(df)


# Province + Year Summary API
@app.route("/api/fires/summary/province-year")
def summary_province_year():
    grouped = (
        df_prov.groupby(["province", "year"])
        .agg(
            fire_count=("latitude", "count"),
            avg_frp=("frp", "mean"),
            avg_confidence=("confidence", "mean"),
        )
        .reset_index()
        .sort_values(["province", "year"])
    )

    return jsonify(
        {"success": True, "count": len(grouped), "data": grouped.to_dict("records")}
    )


from flask import request, jsonify
import pandas as pd

# Assuming df is already loaded


# Get all fires with pagination
# http://localhost:5000/api/fires?page=1&per_page=50
# http://localhost:5000/api/fires?page=2&per_page=100
@app.route("/api/fires", methods=["GET"])
def get_all_fires():
    """Get all fire data with pagination"""
    try:
        # Convert to list of dictionaries
        data = df.to_dict("records")

        # Get pagination parameters
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=10, type=int)

        # Calculate start and end indices
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page

        # Slice the data for pagination
        paginated_data = data[start_idx:end_idx]

        return jsonify(
            {
                "success": True,
                "count": len(paginated_data),
                "total": len(data),
                "data": paginated_data,
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# get all fires -raw data - Filtered bt date
@app.route("/api/fires-date", methods=["GET"])
def get_all_fires_date():
    """Get all fire data with optional date filtering"""
    try:
        # Copy to avoid breaking other endpoints
        filtered_df = df.copy()

        # Read query params
        start_date = request.args.get("startDate")
        end_date = request.args.get("endDate")

        # Apply date filters
        if start_date:
            filtered_df = filtered_df[
                pd.to_datetime(filtered_df["acq_date"]) >= pd.to_datetime(start_date)
            ]

        if end_date:
            filtered_df = filtered_df[
                pd.to_datetime(filtered_df["acq_date"]) <= pd.to_datetime(end_date)
            ]

        return jsonify(
            {
                "success": True,
                "count": len(filtered_df),
                "data": filtered_df.to_dict("records"),
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# yearly fire summary
@app.route("/api/fires/summary/year", methods=["GET"])
def get_summary_by_year():
    """Get fire summary grouped by year"""
    try:
        # Extract year from acq_date
        df["year"] = pd.to_datetime(df["acq_date"]).dt.year

        yearly_summary = (
            df.groupby("year")
            .agg(
                fire_count=("latitude", "count"),
                avg_frp=("frp", "mean"),
                avg_confidence=("confidence", "mean"),
                fire_day_count=("daynight", lambda x: (x == "D").sum()),
                fire_night_count=("daynight", lambda x: (x == "N").sum()),
            )
            .reset_index()
            .sort_values("year")
        )

        data = yearly_summary.to_dict("records")

        return jsonify({"success": True, "count": len(data), "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/fires/filter", methods=["GET"])
def filter_fires():
    """Filter fires with query parameters"""
    try:
        filtered_df = df.copy()

        # Get query parameters
        min_confidence = request.args.get("min_confidence", type=float)
        max_confidence = request.args.get("max_confidence", type=float)
        min_frp = request.args.get("min_frp", type=float)
        max_frp = request.args.get("max_frp", type=float)
        satellite = request.args.get("satellite")
        daynight = request.args.get("daynight")
        date = request.args.get("date")

        # Apply filters
        if min_confidence is not None:
            filtered_df = filtered_df[filtered_df["confidence"] >= min_confidence]
        if max_confidence is not None:
            filtered_df = filtered_df[filtered_df["confidence"] <= max_confidence]
        if min_frp is not None:
            filtered_df = filtered_df[filtered_df["frp"] >= min_frp]
        if max_frp is not None:
            filtered_df = filtered_df[filtered_df["frp"] <= max_frp]
        if satellite:
            filtered_df = filtered_df[filtered_df["satellite"] == satellite]
        if daynight:
            filtered_df = filtered_df[filtered_df["daynight"] == daynight]
        if date:
            filtered_df = filtered_df[filtered_df["acq_date"] == date]

        # Sort if requested
        sort_by = request.args.get("sort_by")
        sort_order = request.args.get("sort_order", "asc")
        if sort_by and sort_by in df.columns:
            filtered_df = filtered_df.sort_values(
                by=sort_by, ascending=(sort_order == "asc")
            )

        # Pagination
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 50, type=int)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page

        total_items = len(filtered_df)
        paginated_df = filtered_df.iloc[start_idx:end_idx]

        data = paginated_df.to_dict("records")

        return jsonify(
            {
                "success": True,
                "page": page,
                "per_page": per_page,
                "total_items": total_items,
                "total_pages": (total_items + per_page - 1) // per_page,
                "data": data,
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/fires/top/<metric>", methods=["GET"])
def get_top_fires(metric):
    """Get top N fires by metric (brightness or frp)"""
    try:
        if metric not in ["brightness", "frp"]:
            return (
                jsonify(
                    {"success": False, "error": 'Metric must be "brightness" or "frp"'}
                ),
                400,
            )

        n = request.args.get("n", 10, type=int)
        top_df = df.nlargest(n, metric)

        data = top_df.to_dict("records")

        return jsonify(
            {"success": True, "metric": metric, "count": len(data), "data": data}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/fires/by_date", methods=["GET"])
def get_fires_by_date():
    """Get fires grouped by date"""
    try:
        grouped = (
            df.groupby("acq_date")
            .agg(
                {
                    "frp": "sum",
                    "brightness": "mean",
                    "confidence": "mean",
                    "latitude": "count",
                }
            )
            .reset_index()
        )

        grouped.columns = [
            "date",
            "total_frp",
            "avg_brightness",
            "avg_confidence",
            "fire_count",
        ]

        data = grouped.to_dict("records")

        return jsonify({"success": True, "count": len(data), "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/fires/<int:index>", methods=["GET"])
def get_fire_by_index(index):
    """Get a specific fire by index"""
    try:
        if index < 0 or index >= len(df):
            return jsonify({"success": False, "error": "Index out of range"}), 404

        fire_data = df.iloc[index].to_dict()
        return jsonify({"success": True, "data": fire_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/fires/search", methods=["GET"])
def search_fires():
    """Search fires by coordinates or date"""
    try:
        lat = request.args.get("lat", type=float)
        lon = request.args.get("lon", type=float)
        date = request.args.get("date")
        tolerance = request.args.get("tolerance", 0.01, type=float)

        filtered_df = df.copy()

        if lat is not None and lon is not None:
            # Search by approximate coordinates
            filtered_df = filtered_df[
                (abs(filtered_df["latitude"] - lat) <= tolerance)
                & (abs(filtered_df["longitude"] - lon) <= tolerance)
            ]

        if date:
            filtered_df = filtered_df[filtered_df["acq_date"] == date]

        data = filtered_df.to_dict("records")

        return jsonify({"success": True, "count": len(data), "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Reporting
@app.route("/report")
def report():
    return render_template(
        "analytics/fire_bulletin.html",
        report_month="August",
        report_year=2025,
        fire_stats={
            "total_fires": 18432,
            "top_provinces": ["Zambezia", "Katanga", "Eastern Province"],
        },
        province_fire_counts=[
            {"province": "DRC", "count": 5200},
            {"province": "Mozambique", "count": 4100},
            {"province": "Zambia", "count": 3600},
        ],
        bar_chart={
            "labels": ["Midlands", "Mat North", "Harare", "Bulawayo"],
            "values": [5200, 4100, 3600, 950],
        },
        time_series={
            "dates": ["2025-08-01", "2025-08-02", "2025-08-03"],
            "counts": [320, 450, 610],
            "max_fires": 610,
            "peak_date": "2025-08-03",
        },
        weather_data=[
            {"location": "Harare", "temperature": 29, "rainfall": 0, "wind_speed": 3.2},
            {"location": "Gweru", "temperature": 31, "rainfall": 1, "wind_speed": 4.1},
            {"location": "Mutare", "temperature": 28, "rainfall": 0, "wind_speed": 5.0},
        ],
    )


if __name__ == "__main__":
    app.run(debug=True)
