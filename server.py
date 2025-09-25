from flask import Flask, request, jsonify
from flask_cors import CORS
import xmltodict

app = Flask(__name__)
CORS(app)

@app.route("/upload-event", methods=["POST"])
def upload_event():
    if 'xmlFile' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"})

    xml_file = request.files['xmlFile']
    try:
        xml_content = xml_file.read()
        data = xmltodict.parse(xml_content)

        # Initialize stats dict
        stats = {}

        # Robust parsing: check for "stats" key
        stats_data = data.get("stats", {})
        if isinstance(stats_data, dict):
            for key, value in stats_data.items():
                # If value is a dict (xmltodict wraps text in '#text'), get '#text'
                if isinstance(value, dict) and "#text" in value:
                    value = value["#text"]
                try:
                    stats[key] = float(value)
                except:
                    stats[key] = 0
        else:
            # stats_data is empty or malformed
            stats = {}

        return jsonify({"success": True, "stats": stats})

    except Exception as e:
        print("XML parse error:", e)
        return jsonify({"success": False, "error": "Failed to parse XML"})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
