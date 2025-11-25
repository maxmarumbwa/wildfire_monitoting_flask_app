from flask import Flask, render_template, jsonify
import json, os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/fire_hotspots')
def fire_hotspots():
    fp = os.path.join(app.root_path, 'data', 'fire_hotspot.json')
    with open(fp) as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
