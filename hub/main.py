import os
import json
import glob

from flask import Flask, jsonify

data_dir = os.environ.get('HUB_DATA_DIR', './data')
port = int(os.environ.get('HUB_PORT', 8080))
app = Flask(__name__)

@app.route('/screens')
def get_screens():
    files = sorted(glob.glob(data_dir + '/*.json'))
    screens = []

    for filepath in files:
        with open(filepath) as f:
            data = json.load(f)
        screen_id = os.path.basename(filepath).replace('.json', '')
        screens.append({
            "id": screen_id,
            "updated_at": data["updated_at"],
            "lines": data["lines"]
        })
    return jsonify(screens)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)