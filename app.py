from flask import Flask, render_template, jsonify
import json, os

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/fire_hotspots")
def fire_hotspots():
    fp = os.path.join(app.root_path, "data", "fire_hotspot.json")
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


if __name__ == "__main__":
    app.run(debug=True)
