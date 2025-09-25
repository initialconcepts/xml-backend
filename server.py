from flask import Flask, request, jsonify
from flask_cors import CORS
import xmltodict

app = Flask(__name__)
CORS(app)

def parse_bsgame_stats(bsgame):
    """
    Convert the bsgame XML dict into a per-team stats dictionary.
    """
    team_stats = {}

    try:
        # Navigate to plays → inning → batting
        innings = bsgame.get('bsgame', {}).get('plays', {}).get('inning', [])
        if not isinstance(innings, list):
            innings = [innings]

        for inning in innings:
            batting_list = inning.get('batting', [])
            if not isinstance(batting_list, list):
                batting_list = [batting_list]

            for batting in batting_list:
                team_name = batting.get('@team') or batting.get('@name') or "Unknown Team"
                if team_name not in team_stats:
                    # initialize basic stats
                    team_stats[team_name] = {'AB':0,'R':0,'H':0,'RBI':0,'BB':0,'SO':0,'SB':0,'E':0,'LOB':0}

                plays = batting.get('play', [])
                if not isinstance(plays, list):
                    plays = [plays]

                for play in plays:
                    # Example: add simple dummy counts; adapt based on your XML structure
                    batter = play.get('batter', {})
                    # This depends on your XML keys
                    for stat in ['AB','R','H','RBI','BB','SO','SB','E','LOB']:
                        val = batter.get(f"@{stat}", 0)
                        try: val = int(val)
                        except: val = 0
                        team_stats[team_name][stat] += val

    except Exception as e:
        print("Error parsing bsgame stats:", e)

    return team_stats

@app.route("/upload-event", methods=["POST"])
def upload_event():
    if 'xmlFile' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"})

    xml_file = request.files['xmlFile']
    try:
        xml_content = xml_file.read()
        data = xmltodict.parse(xml_content)

        # Parse stats by team
        stats = parse_bsgame_stats(data)

        return jsonify({"success": True, "stats": stats})

    except Exception as e:
        print("XML parse error:", e)
        return jsonify({"success": False, "error": "Failed to parse XML"})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
