from flask import Flask, render_template, jsonify, request, session
import json, os
import requests
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
@app.route("/getfwi_1point")
def home():
    return render_template("getfwi_1point.html")


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
