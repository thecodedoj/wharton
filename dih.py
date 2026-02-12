import csv
import json
import math

# Read CSV file and convert to list of dictionaries
with open('whl_2025 - whl_2025_sorted.csv', mode='r') as file:
    csv_reader = csv.DictReader(file)
    data = [row for row in csv_reader]

# Convert to JSON string
json_string = json.dumps(data, indent=4)
def calculate_elo(json_input, k_factor=40):
    # --- CONFIGURATION ---
    STARTING_ELO = 1500.0  # Midpoint of 500-2500
    MIN_ELO = 500.0
    MAX_ELO = 2500.0
    
    # 1. Initialize ratings dictionary
    ratings = {} 

    try:
        data = json.loads(json_input)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON format: {e}")
        return

    # 2. Group records by game_id
    games = {}
    for record in data:
        g_id = record.get('game_id')
        if not g_id: continue 
        
        if g_id not in games:
            games[g_id] = []
        games[g_id].append(record)

    print(f"{'GAME ID':<10} {'MATCHUP':<30} {'SCORE':<10} {'CHANGE':<10} {'NEW RATINGS'}")
    print("-" * 85)

    # 3. Process each game
    for g_id, segments in games.items():
        # Basic info
        home_team = segments[0].get('home_team', 'Unknown')
        away_team = segments[0].get('away_team', 'Unknown')
        went_ot = int(segments[0].get('went_ot', 0))

        # Aggregate stats
        h_goals = sum(int(s.get('home_goals', 0)) for s in segments)
        a_goals = sum(int(s.get('away_goals', 0)) for s in segments)

        # Get current ratings (Default to 1500)
        r_home = ratings.get(home_team, STARTING_ELO)
        r_away = ratings.get(away_team, STARTING_ELO)

        # --- ELO CALCULATION ---
        
        # 1. Expected Score
        # Divisor 400 is standard. 
        expected_home = 1 / (1 + 10 ** ((r_away - r_home) / 400))

        # 2. Actual Score
        if h_goals > a_goals:
            actual_score = 1.0
        elif h_goals < a_goals:
            actual_score = 0.0
        else:
            actual_score = 0.5

        # 3. Margin of Victory Multiplier
        # Logarithmic scale: 1 goal diff = 1.0x, 5 goal diff = ~2.6x
        margin = abs(h_goals - a_goals)
        mov_multiplier = math.log(margin + 1) if margin > 0 else 1

        # 4. K-Factor Adjustment
        # Reduce impact if game went to OT
        current_k = k_factor * 0.8 if went_ot else k_factor

        # 5. Calculate Change
        elo_change = current_k * mov_multiplier * (actual_score - expected_home)

        # --- UPDATE & CLAMP RATINGS ---
        new_home = r_home + elo_change
        new_away = r_away - elo_change

        # Clamp between 500 and 2500
        ratings[home_team] = max(MIN_ELO, min(MAX_ELO, new_home))
        ratings[away_team] = max(MIN_ELO, min(MAX_ELO, new_away))

        # Log output
        matchup_str = f"{home_team} vs {away_team}"
        score_str = f"{h_goals}-{a_goals}"
        new_rating_str = f"H:{ratings[home_team]:.0f} A:{ratings[away_team]:.0f}"
        print(f"{g_id:<10} {matchup_str:<30} {score_str:<10} {elo_change:<+10.2f} {new_rating_str}")

    # 4. Final Standings
    print("\n" + "="*40)
    print(f"FINAL STANDINGS (Scale: {MIN_ELO}-{MAX_ELO})")
    print("="*40)
    sorted_ratings = sorted(ratings.items(), key=lambda item: item[1], reverse=True)
    for rank, (team, rating) in enumerate(sorted_ratings, 1):
        print(f"{rank}. {team:<20} {rating:.2f}")

    return ratings

    return dict(current_ratings)     
calculate_elo(json_string)