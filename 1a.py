import csv 
import json 
def cast(row):
    return {
        **row,
        "toi": float(row["toi"]),
        "home_goals": int(row["home_goals"]),
        "away_goals": int(row["away_goals"]),
        "went_ot": bool(int(row["went_ot"]))
    }
with open("whl_2025 - whl_2025.csv", newline = "", encoding="utf-8") as f:
    reader   = csv.DictReader(f)
    rows = [cast(row) for row in reader]
    

json_dih = json.dumps(rows, indent=2)
data = json.loads(json_dih) 

teams = set()

for team in data:
    teams.add(team["home_team"])
    teams.add(team["away_team"])

print(teams)


