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

        # Example XML: <stats><Points>20</Points><Assists>5</Assists></stats>
        stats = {}
        if "stats" in data:
            for key, value in data["stats"].items():
                try:
                    stats[key] = float(value)
                except:
                    stats[key] = 0

        return jsonify({"success": True, "stats": stats})
    except Exception as e:
        print("XML parse error:", e)
        return jsonify({"success": False, "error": "Failed to parse XML"})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
