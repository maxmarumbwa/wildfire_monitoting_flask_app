from flask import Flask, render_template, jsonify, send_file
import os

app = Flask(__name__)


@app.route("/")
def index():
    # List available GeoJSON files
    geojson_files = []
    data_folder = "data"

    if os.path.exists(data_folder):
        for file in os.listdir(data_folder):
            if file.endswith(".geojson"):
                geojson_files.append(file)

    return render_template("map.html", geojson_files=geojson_files)


@app.route("/data/<filename>")
def get_geojson(filename):
    # Serve GeoJSON files securely
    safe_filename = os.path.basename(filename)
    filepath = os.path.join("data", safe_filename)

    if os.path.exists(filepath) and safe_filename.endswith(".geojson"):
        return send_file(filepath, mimetype="application/json")
    else:
        return jsonify({"error": "File not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
