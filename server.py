from flask import Flask, request, jsonify
from flask_cors import CORS
import xmltodict

app = Flask(__name__)
CORS(app)

def parse_teams_stats(xml_dict):
    stats = {}
    try:
        game = xml_dict.get('bsgame', {})
        linescores = game.get('linescore', {})
        teams = linescores.get('team', [])
        if isinstance(teams, dict):
            teams = [teams]

        for team in teams:
            name = team.get('@name', 'Unknown Team')
            stats[name] = {
                'AB': int(team.get('AB', 0)),
                'R': int(team.get('R', 0)),
                'H': int(team.get('H', 0)),
                'RBI': int(team.get('RBI', 0)),
                'BB': int(team.get('BB', 0)),
                'SO': int(team.get('SO', 0)),
                'SB': int(team.get('SB', 0)),
                'E': int(team.get('E', 0)),
                'LOB': int(team.get('LOB', 0)),
            }
    except Exception as e:
        print("Error parsing team stats:", e)
    return stats

@app.route("/upload-event", methods=["POST"])
def upload_event():
    if 'xmlFile' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"})

    xml_file = request.files['xmlFile']
    try:
        xml_content = xml_file.read()
        data = xmltodict.parse(xml_content)
        stats = parse_teams_stats(data)  # Use the safe team stats parser

        if not stats:
            return jsonify({"success": False, "error": "No team stats found in XML"})

        return jsonify({"success": True, "stats": stats})

    except Exception as e:
        print("XML parse error:", e)
        return jsonify({"success": False, "error": "Failed to parse XML"})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
