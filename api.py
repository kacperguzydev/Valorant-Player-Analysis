# api.py
import requests
import urllib.parse
from datetime import datetime
import pytz
from config import RIOT, logger
from monitoring import track_api_request

@track_api_request
def get_matches():
    region = RIOT['region']
    name = RIOT['name']
    tag = RIOT['tag']
    api_key = RIOT['api_key']
    match_count = RIOT['match_count']
    local_tz = pytz.timezone(RIOT['timezone'])
    encoded_name = urllib.parse.quote(name)
    encoded_tag = urllib.parse.quote(tag)

    url = f"https://api.henrikdev.xyz/valorant/v1/stored-matches/{region}/{encoded_name}/{encoded_tag}?size={match_count}"
    headers = {"Authorization": api_key}
    logger.info(f"Requesting match data from: {url}")

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            matches = response.json().get("data", [])
            if not matches:
                logger.warning("No matches found for the given user.")
                return "No matches found."
            match_data = []
            for match in matches:
                meta = match.get("meta", {})
                stats = match.get("stats", {})
                teams = match.get("teams", {})
                match_info = {
                    "match_id": meta.get('id'),
                    "map_name": meta.get('map', {}).get('name'),
                    "mode": meta.get('mode'),
                    "game_start": meta.get('started_at'),
                }
                if meta.get('started_at'):
                    utc_dt = datetime.fromisoformat(meta['started_at'].replace("Z", "+00:00"))
                    local_dt = utc_dt.astimezone(local_tz)
                    match_info["game_start_local"] = local_dt.strftime('%Y-%m-%d %H:%M:%S')
                red_score = teams.get("red", 0)
                blue_score = teams.get("blue", 0)
                winning_team = ("Red" if red_score > blue_score
                                else "Blue" if blue_score > red_score
                                else "Draw/Unknown")
                player_team = stats.get("team")
                result = "Win" if player_team == winning_team else "Loss"

                match_info.update({
                    "winning_team": winning_team,
                    "agent": stats.get('character', {}).get('name'),
                    "team": player_team,
                    "puuid": stats.get('puuid'),
                    "kills": stats.get('kills'),
                    "deaths": stats.get('deaths'),
                    "assists": stats.get('assists'),
                    "score": stats.get('score'),
                    "damage": stats.get('damage', {}).get('made'),
                    "result": result
                })
                match_data.append(match_info)
            return match_data
        else:
            logger.error(f"API Request failed: {response.status_code}")
            return f"[ERROR] {response.status_code}: {response.text}"
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return f"Request failed: {e}"
