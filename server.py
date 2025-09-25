from flask import Flask, request, jsonify
from flask_cors import CORS
import xmltodict

app = Flask(__name__)
CORS(app)

def safe_int(value):
    """Convert to int safely, default 0"""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0

def parse_teams_stats(xml_dict):
    stats = {}
    try:
        game = xml_dict.get('bsgame', {})
        linescores = game.get('linescore', {})
        teams = linescores.get('team', [])

        # Ensure teams is a list
        if isinstance(teams, dict):
            teams = [teams]

        for team in teams:
            name = team.get('@name', 'Unknown Team')
            
            # Some XML has totals nested inside <totals> tags
            totals = team.get('totals', {})
            hitting = totals.get('hitting', {})
            fielding = totals.get('fielding', {})

            stats[name] = {
                'AB': safe_int(hitting.get('@ab')),
                'R': safe_int(hitting.get('@r')),
                'H': safe_int(hitting.get('@h')),
                'RBI': safe_int(hitting.get('@rbi')),
                'BB': safe_int(hitting.get('@bb')),
                'SO': safe_int(hitting.get('@so')),
                'SB': safe_int(hitting.get('@sb')),
                'E': safe_int(fielding.get('@e')),
                'LOB': safe_int(team.get('@LOB'))  # sometimes LOB is directly under team
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
        stats = parse_teams_stats(data)

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
