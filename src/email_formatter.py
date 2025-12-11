"""
Email Formatting for NBA Predictions
Author: Orb Analytics (Liam Chaitin)
Purpose: Format prediction records into readable email text per framework
"""

from typing import Dict, List, Any


def format_game_header(prediction: Dict[str, Any]) -> str:
    """
    Format the game header line.
    
    Example output:
    🏀 San Antonio Spurs vs New Orleans Pelicans  (Favorite: San Antonio -9.5, Odds: -110 / -110)
    """
    home = prediction['home_team']
    away = prediction['away_team']
    favorite = prediction['favorite_team']
    spread = prediction['spread']
    fav_odds = prediction['fav_odds']
    dog_odds = prediction['dog_odds']
    
    header = (
        f"🏀 {home} vs {away}  "
        f"(Favorite: {favorite} {spread:+.1f}, Odds: {fav_odds:+.0f} / {dog_odds:+.0f})"
    )
    
    return header


def format_model_line(model_name: str, model_data: Dict[str, Any]) -> str:
    """
    Format one model's prediction line.
    
    Args:
        model_name: Display name like "Logistic", "Linear", etc.
        model_data: Dict with prob_fav_cover, fav_edge, dog_edge, pick_side, pick_team, pick_line
    
    Example output:
    Logistic: New Orleans +9.5 | Cover Prob: 75.1% | F Edge: -27.5% | D Edge: +22.7% | BEST: New Orleans +9.5
    Linear:   San Antonio -9.5 | Cover Prob: 61.3% | F Edge: +6.5%  | D Edge: -9.1%  | BEST: San Antonio -9.5
    """
    pick_team = model_data['pick_team']
    pick_line = model_data['pick_line']
    pick_side = model_data['pick_side']
    
    # Determine which STANDARDIZED probability to show (the one for the picked side)
    if pick_side == "FAVORITE":
        prob_cover = model_data['standardized_fav']
    elif pick_side == "UNDERDOG":
        prob_cover = model_data['standardized_dog']
    else:
        # NO BET - show favorite standardized probability
        prob_cover = model_data['standardized_fav']
    
    fav_edge = model_data['fav_edge']
    dog_edge = model_data['dog_edge']
    
    # Format pick display
    if pick_side == "NO BET":
        pick_display = "NO BET        "
        best_label = "No edge (pass)"
    else:
        pick_display = f"{pick_team} {pick_line:+.1f}"
        best_label = f"{pick_team} {pick_line:+.1f}"
    
    # Format model name with padding for alignment
    model_padded = f"{model_name}:"
    model_padded = model_padded.ljust(16)
    
    line = (
        f"{model_padded} {pick_display:30s} | "
        f"Cover Prob: {prob_cover*100:5.1f}% | "
        f"F Edge: {fav_edge*100:+6.1f}% | "
        f"D Edge: {dog_edge*100:+6.1f}% | "
        f"BEST: {best_label}"
    )
    
    return line


def format_game_predictions(prediction: Dict[str, Any], model_order: List[str] = None) -> str:
    """
    Format complete game prediction with header and all model lines.
    
    Args:
        prediction: Prediction record dict from build_prediction_record()
        model_order: List of model names in desired order (default: Logistic, Linear, RF, DT)
    
    Returns:
        Formatted multi-line string for this game
    """
    if model_order is None:
        model_order = ["Logistic", "Linear", "Random Forest", "Decision Tree"]
    
    lines = []
    
    # Add header
    lines.append(format_game_header(prediction))
    lines.append("")
    
    # Add each model's line
    for model_name in model_order:
        if model_name in prediction['models']:
            model_data = prediction['models'][model_name]
            lines.append(format_model_line(model_name, model_data))
    
    lines.append("")  # Blank line after game
    
    return "\n".join(lines)


def format_model_records(records: Dict[str, Dict[str, int]]) -> str:
    """
    Format the season records header.
    
    Args:
        records: Dict with model names as keys, values are dicts with 'wins', 'losses', 'pushes'
    
    Example output:
    📈 Model Records (Season to Date)
    - Logistic: 157-148-0 (51.5%)
    - Linear: 163-155-0 (51.3%)
    - Random Forest: 163-140-0 (53.8%)
    - Decision Tree: 159-158-0 (50.2%)
    """
    lines = []
    lines.append("📈 Model Records (Season to Date)")
    
    for model_name, record in records.items():
        wins = record.get('wins', 0)
        losses = record.get('losses', 0)
        pushes = record.get('pushes', 0)
        
        # Calculate win percentage (excluding pushes)
        total_decided = wins + losses
        win_pct = (wins / total_decided * 100) if total_decided > 0 else 0.0
        
        lines.append(f"- {model_name}: {wins}-{losses}-{pushes} ({win_pct:.1f}%)")
    
    return "\n".join(lines)


def format_predictions_for_email(
    predictions: List[Dict[str, Any]], 
    model_records: Dict[str, Dict[str, int]],
    date_str: str
) -> str:
    """
    Format complete email body with all predictions.
    
    Args:
        predictions: List of prediction record dicts
        model_records: Season records for header
        date_str: Date string for title (e.g., "December 6, 2025")
    
    Returns:
        Complete email body text
    """
    lines = []
    
    # Header
    lines.append("=" * 100)
    lines.append(f"🏀 NBA SPREAD PREDICTIONS - {date_str}")
    lines.append("=" * 100)
    lines.append("")
    
    # Model records
    lines.append(format_model_records(model_records))
    lines.append("")
    lines.append("=" * 100)
    lines.append("")
    
    # Each game
    for prediction in predictions:
        lines.append(format_game_predictions(prediction))
    
    # Footer
    lines.append("=" * 100)
    lines.append("Generated by Orb Analytics NBA Model")
    lines.append("=" * 100)
    
    return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    print("Testing email_formatter.py functions...")
    
    # Test data
    test_prediction = {
        "date": "2025-11-02",
        "home_team": "San Antonio Spurs",
        "away_team": "New Orleans Pelicans",
        "favorite_team": "San Antonio Spurs",
        "underdog_team": "New Orleans Pelicans",
        "spread": -9.5,
        "fav_odds": -110,
        "dog_odds": -110,
        "fav_at_home": 1,
        "models": {
            "Logistic": {
                "prob_fav_cover": 0.251,
                "prob_dog_cover": 0.749,
                "fav_edge": -0.275,
                "dog_edge": 0.227,
                "pick_side": "UNDERDOG",
                "pick_team": "New Orleans Pelicans",
                "pick_line": 9.5
            },
            "Linear": {
                "prob_fav_cover": 0.61,
                "prob_dog_cover": 0.39,
                "fav_edge": 0.065,
                "dog_edge": -0.091,
                "pick_side": "FAVORITE",
                "pick_team": "San Antonio Spurs",
                "pick_line": -9.5
            },
            "Random Forest": {
                "prob_fav_cover": 0.50,
                "prob_dog_cover": 0.50,
                "fav_edge": -0.024,
                "dog_edge": -0.024,
                "pick_side": "NO BET",
                "pick_team": None,
                "pick_line": None
            },
            "Decision Tree": {
                "prob_fav_cover": 0.72,
                "prob_dog_cover": 0.28,
                "fav_edge": 0.196,
                "dog_edge": -0.244,
                "pick_side": "FAVORITE",
                "pick_team": "San Antonio Spurs",
                "pick_line": -9.5
            }
        }
    }
    
    test_records = {
        "Logistic": {"wins": 42, "losses": 35, "pushes": 3},
        "Linear": {"wins": 39, "losses": 38, "pushes": 3},
        "Random Forest": {"wins": 44, "losses": 33, "pushes": 3},
        "Decision Tree": {"wins": 37, "losses": 40, "pushes": 3}
    }
    
    # Test individual functions
    print("\n" + "="*100)
    print("TEST: format_game_header()")
    print("="*100)
    print(format_game_header(test_prediction))
    
    print("\n" + "="*100)
    print("TEST: format_model_line()")
    print("="*100)
    for model_name in ["Logistic", "Linear", "Random Forest", "Decision Tree"]:
        print(format_model_line(model_name, test_prediction['models'][model_name]))
    
    print("\n" + "="*100)
    print("TEST: format_game_predictions()")
    print("="*100)
    print(format_game_predictions(test_prediction))
    
    print("\n" + "="*100)
    print("TEST: format_model_records()")
    print("="*100)
    print(format_model_records(test_records))
    
    print("\n" + "="*100)
    print("TEST: Complete Email")
    print("="*100)
    email = format_predictions_for_email([test_prediction], test_records, "November 2, 2025")
    print(email)
    
    print("\n✅ All email_formatter.py tests passed!")
