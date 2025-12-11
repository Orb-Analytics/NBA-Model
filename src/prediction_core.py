"""
NBA Prediction Core - Data Structure & Edge Calculation
Author: Orb Analytics (Liam Chaitin)
Purpose: Core functions for building prediction records and computing edges per framework
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Any


def american_to_prob(odds: float) -> float:
    """
    Convert American odds to implied probability.
    
    Args:
        odds: American odds (e.g., -110, +150)
    
    Returns:
        Implied probability as decimal (e.g., 0.523)
    """
    if odds < 0:
        return (-odds) / ((-odds) + 100.0)
    else:
        return 100.0 / (odds + 100.0)


def build_prediction_record(game_row: pd.Series, model_predictions: Dict[str, float]) -> Dict[str, Any]:
    """
    Build standardized prediction record for a single game.
    
    Args:
        game_row: Pandas Series with game data from master dataset
        model_predictions: Dict with keys like 'logistic', 'linear', etc. 
                          Values are prob_fav_cover (favorite-centric probability)
    
    Returns:
        Prediction record dict following framework data contract
    """
    # Extract basic game info
    date = pd.to_datetime(game_row['Date']).strftime('%Y-%m-%d')
    favorite_team = str(game_row['Favorite'])
    underdog_team = str(game_row['Underdog'])
    spread = float(game_row['Spread'])  # Always in favorite terms (negative)
    
    # Determine home/away
    fav_at_home = int(game_row.get('Fav. At Home?', 0))
    if fav_at_home == 1:
        home_team = favorite_team
        away_team = underdog_team
    else:
        home_team = underdog_team
        away_team = favorite_team
    
    # Get odds (default to -110 if missing per framework)
    fav_odds = float(game_row.get('Fav. Odds', -110))
    dog_odds = float(game_row.get('Dog Odds', -110))
    
    # Handle missing odds
    if pd.isna(fav_odds):
        fav_odds = -110
    if pd.isna(dog_odds):
        dog_odds = -110
    
    # Build models dict with edge calculations
    models_dict = {}
    
    for model_name, prob_fav_cover in model_predictions.items():
        model_dict = compute_model_pick(
            prob_fav_cover=prob_fav_cover,
            fav_odds=fav_odds,
            dog_odds=dog_odds,
            favorite_team=favorite_team,
            underdog_team=underdog_team,
            spread=spread
        )
        models_dict[model_name] = model_dict
    
    # Build complete prediction record
    prediction_record = {
        "date": date,
        "home_team": home_team,
        "away_team": away_team,
        "favorite_team": favorite_team,
        "underdog_team": underdog_team,
        "spread": spread,
        "fav_odds": fav_odds,
        "dog_odds": dog_odds,
        "fav_at_home": fav_at_home,
        "models": models_dict
    }
    
    return prediction_record


def compute_model_pick(
    prob_fav_cover: float,
    fav_odds: float,
    dog_odds: float,
    favorite_team: str,
    underdog_team: str,
    spread: float
) -> Dict[str, Any]:
    """
    Compute edges and pick for a single model using STANDARDIZED probabilities.
    
    Standardization Formula:
    - Standardized Prob = (Model Prob × 0.35) + (Implied Prob × 0.65)
    - Edge = Standardized Prob - Implied Prob
    
    Args:
        prob_fav_cover: Model's probability that favorite covers (0-1)
        fav_odds: American odds for favorite (e.g., -110)
        dog_odds: American odds for underdog (e.g., -110)
        favorite_team: Name of favorite team
        underdog_team: Name of underdog team
        spread: Spread in favorite terms (e.g., -9.5)
    
    Returns:
        Dict with prob_fav_cover, prob_dog_cover, standardized probs, fav_edge, dog_edge, 
        pick_side, pick_team, pick_line
    """
    # Calculate dog probability (raw from model)
    prob_dog_cover = 1.0 - prob_fav_cover
    
    # Convert odds to implied probabilities
    implied_fav = american_to_prob(fav_odds)
    implied_dog = american_to_prob(dog_odds)
    
    # STANDARDIZE probabilities: 35% model + 65% market
    standardized_fav = (prob_fav_cover * 0.35) + (implied_fav * 0.65)
    standardized_dog = (prob_dog_cover * 0.35) + (implied_dog * 0.65)
    
    # Calculate edges using STANDARDIZED probabilities
    fav_edge = standardized_fav - implied_fav
    dog_edge = standardized_dog - implied_dog
    
    # Pick logic: select side with highest edge, or NO BET if both negative
    if max(fav_edge, dog_edge) <= 0:
        pick_side = "NO BET"
        pick_team = None
        pick_line = None
    else:
        if fav_edge >= dog_edge:
            pick_side = "FAVORITE"
            pick_team = favorite_team
            pick_line = -spread  # Favorite gets negative spread (e.g., -9.5)
        else:
            pick_side = "UNDERDOG"
            pick_team = underdog_team
            pick_line = spread  # Underdog gets positive spread (e.g., +9.5)
    
    return {
        "prob_fav_cover": prob_fav_cover,  # Raw model probability
        "prob_dog_cover": prob_dog_cover,  # Raw model probability
        "standardized_fav": standardized_fav,  # Standardized probability
        "standardized_dog": standardized_dog,  # Standardized probability
        "fav_edge": fav_edge,  # Edge calculated from standardized prob
        "dog_edge": dog_edge,  # Edge calculated from standardized prob
        "pick_side": pick_side,
        "pick_team": pick_team,
        "pick_line": pick_line
    }


# Example usage and validation
if __name__ == "__main__":
    print("Testing prediction_core.py functions...")
    
    # Test american_to_prob
    assert abs(american_to_prob(-110) - 0.5238) < 0.001
    assert abs(american_to_prob(110) - 0.4762) < 0.001
    print("✅ american_to_prob tests passed")
    
    # Test compute_model_pick
    result = compute_model_pick(
        prob_fav_cover=0.65,
        fav_odds=-110,
        dog_odds=-110,
        favorite_team="San Antonio Spurs",
        underdog_team="New Orleans Pelicans",
        spread=-9.5
    )
    print(f"✅ compute_model_pick test: {result}")
    assert result['pick_side'] == "FAVORITE"
    assert result['pick_team'] == "San Antonio Spurs"
    assert result['pick_line'] == -9.5
    
    # Test with underdog edge
    result2 = compute_model_pick(
        prob_fav_cover=0.25,
        fav_odds=-110,
        dog_odds=-110,
        favorite_team="San Antonio Spurs",
        underdog_team="New Orleans Pelicans",
        spread=-9.5
    )
    print(f"✅ compute_model_pick test 2: {result2}")
    assert result2['pick_side'] == "UNDERDOG"
    assert result2['pick_team'] == "New Orleans Pelicans"
    assert result2['pick_line'] == 9.5
    
    # Test NO BET
    result3 = compute_model_pick(
        prob_fav_cover=0.50,
        fav_odds=-110,
        dog_odds=-110,
        favorite_team="San Antonio Spurs",
        underdog_team="New Orleans Pelicans",
        spread=-9.5
    )
    print(f"✅ compute_model_pick test 3 (NO BET): {result3}")
    assert result3['pick_side'] == "NO BET"
    
    print("\n✅ All prediction_core.py tests passed!")
