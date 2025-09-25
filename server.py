from flask import Flask, request, jsonify
from flask_cors import CORS
import xmltodict

app = Flask(__name__)
CORS(app)

def extract_stats(obj):
    """
    Recursively extract all numeric stats from XML parsed dict.
    Returns a flat dict of key-value pairs.
    """
    stats = {}

    if isinstance(obj, dict):
        for k, v in obj.items():
            # If value is a dict with '#text', unwrap it
            if isinstance(v, dict) and '#text' in v:
                try:
                    stats[k] = float(v['#text'])
                except:
                    stats[k] = 0
            elif isinstance(v, dict) or isinstance(v, list):
                # Recursively extract from nested dict/list
                nested = extract_stats(v)
                for nk, nv in nested.items():
                    stats[f"{k}.{nk}"] = nv
            else:
                # Attempt to convert directly to float
                try:
                    stats[k] = float(v)
                except:
                    stats[k] = 0
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            nested = extract_stats(item)
            for nk, nv in nested.items():
                stats[f"{idx}.{nk}"] = nv
    return stats

@app.route("/upload-event", methods=["POST"])
def upload_event():
    if 'xmlFile' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"})

    xml_file = request.files['xmlFile']
    try:
        xml_content = xml_file.read()
        print("Raw XML received:", xml_content.decode())  # log for debugging

        data = xmltodict.parse(xml_content)
        print("Parsed XML dict:", data)

        # Extract stats from entire XML
        stats = extract_stats(data)

        return jsonify({"success": True, "stats": stats})

    except Exception as e:
        print("XML parse error:", e)
        return jsonify({"success": False, "error": "Failed to parse XML"})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
