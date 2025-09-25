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

        stats = {}

        # Navigate to teams
        teams = data.get('bsgame', {}).get('team', [])
        if isinstance(teams, dict):
            teams = [teams]  # ensure it's a list

        for team in teams:
            team_name = team.get('@name', 'Unknown Team')
            stats[team_name] = {}

            # Team totals
            totals = team.get('totals', {})
            stats[team_name]['totals'] = {
                'hitting': {k: int(v) for k, v in totals.get('hitting', {}).items()},
                'fielding': {k: int(v) for k, v in totals.get('fielding', {}).items()},
                'pitching': {k: int(v) for k, v in totals.get('pitching', {}).items()},
            }

            # Players
            players = team.get('player', [])
            if isinstance(players, dict):
                players = [players]

            stats[team_name]['players'] = []
            for player in players:
                player_data = {
                    'name': player.get('@name', 'Unknown'),
                    'hitting': {k: int(v) for k, v in player.get('hitting', {}).items()},
                    'fielding': {k: int(v) for k, v in player.get('fielding', {}).items()},
                    'pitching': {k: int(v) for k, v in player.get('pitching', {}).items()},
                }
                stats[team_name]['players'].append(player_data)

        return jsonify({"success": True, "stats": stats})

    except Exception as e:
        print("XML parse error:", e)
        return jsonify({"success": False, "error": "Failed to parse XML"})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
