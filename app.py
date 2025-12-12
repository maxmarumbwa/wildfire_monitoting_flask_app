from flask import Flask, render_template, jsonify, request, session
import json, os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = "dev-secret-key"  # REQUIRED for sessions


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
@app.route("/analytics/hist")
def analytics_hist():
    return render_template("analytics/analytics_hist.html")


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
df = pd.read_csv("static/data/fire1.csv")


@app.context_processor
def inject_fire_data():
    total_detections = len(df)
    avg_frp = df["frp"].mean()
    fire_data = df.to_dict("records")
    return dict(total_detections=total_detections, avg_frp=avg_frp, fire_data=fire_data)


# display results external pages
@app.route("/getfwi_1point_ext")
def weather_ext():
    return render_template("getfwi_1point_ext.html")


@app.route("/coordinates_settings_map")
def coordinates_settings_map():
    return render_template("coordinates_settings_map.html")


@app.route("/get_weather", methods=["POST"])
def get_weather():
    lat = request.form.get("lat")
    lon = request.form.get("lon")

    if not lat or not lon:
        return jsonify({"error": "Missing coordinates"}), 400

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}"

    data = requests.get(url).json()
    return jsonify(data)


# post weather data to external pages
@app.route("/weather_summary")
def weather_summary():
    return render_template("weather_summary.html", weather=session.get("weather"))


@app.route("/save_weather", methods=["POST"])
def save_weather():
    session["weather"] = request.json
    return jsonify({"status": "saved"})


if __name__ == "__main__":
    app.run(debug=True)
