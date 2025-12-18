#!/usr/bin/env python3
"""
Backtest the Standardized & Averaged Model

This script:
1. Loads unified model results (already has all 4 model probabilities)
2. Averages the 4 model probabilities
3. Applies standardization: 35% averaged model + 65% implied probability
4. Calculates edges and makes picks (only when edge >= 3%)
5. Evaluates against actual outcomes
"""

import pandas as pd
import numpy as np
import argparse
from typing import Dict


def american_to_prob(odds: float) -> float:
    """Convert American odds to implied probability."""
    if pd.isna(odds):
        return np.nan
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return abs(odds) / (abs(odds) + 100)


def compute_averaged_pick(
    logistic_prob: float,
    linear_prob: float,
    rf_prob: float,
    tree_prob: float,
    fav_odds: float,
    dog_odds: float,
    min_edge: float = 0.03
) -> Dict:
    """
    Compute the averaged & standardized pick.
    
    Formula:
    - Average all 4 model probabilities
    - Standardized prob = (0.35 * averaged_model_prob) + (0.65 * implied_prob)
    - Edge = standardized_prob - implied_prob
    - Pick only if edge >= min_edge
    
    Returns dict with pick info.
    """
    # Count valid models
    probs = [logistic_prob, linear_prob, rf_prob, tree_prob]
    valid_probs = [p for p in probs if not pd.isna(p)]
    
    if len(valid_probs) == 0:
        return {
            "num_models": 0,
            "averaged_fav_prob": np.nan,
            "standardized_fav": np.nan,
            "standardized_dog": np.nan,
            "fav_edge": np.nan,
            "dog_edge": np.nan,
            "pick_side": "NO BET",
            "pick_team": None,
            "edge": 0.0
        }
    
    # Average model probabilities
    averaged_fav_prob = np.mean(valid_probs)
    averaged_dog_prob = 1 - averaged_fav_prob
    
    # Get implied probabilities
    fav_implied = american_to_prob(fav_odds)
    dog_implied = american_to_prob(dog_odds)
    
    # Apply standardization formula
    standardized_fav = (0.35 * averaged_fav_prob) + (0.65 * fav_implied)
    standardized_dog = (0.35 * averaged_dog_prob) + (0.65 * dog_implied)
    
    # Calculate edges
    fav_edge = standardized_fav - fav_implied
    dog_edge = standardized_dog - dog_implied
    
    # Determine pick - only pick if we have a POSITIVE edge >= min_edge
    if fav_edge >= min_edge and fav_edge > dog_edge:
        pick_side = "FAVORITE"
        edge = fav_edge
    elif dog_edge >= min_edge and dog_edge > fav_edge:
        pick_side = "UNDERDOG"
        edge = dog_edge
    else:
        pick_side = "NO BET"
        edge = max(fav_edge, dog_edge) if not pd.isna(fav_edge) else 0.0
    
    return {
        "num_models": len(valid_probs),
        "averaged_fav_prob": averaged_fav_prob,
        "averaged_dog_prob": averaged_dog_prob,
        "standardized_fav": standardized_fav,
        "standardized_dog": standardized_dog,
        "fav_edge": fav_edge,
        "dog_edge": dog_edge,
        "pick_side": pick_side,
        "pick_team": None,  # Will be filled in later
        "edge": edge
    }


def backtest(
    unified_path: str = 'data/unified_model_results.csv',
    start_date: str = '2025-10-23',
    end_date: str = '2025-12-18',
    min_edge: float = 0.03
) -> pd.DataFrame:
    """Run the backtest."""
    
    print("=" * 100)
    print("🔬 BACKTESTING STANDARDIZED & AVERAGED MODEL")
    print("=" * 100)
    print(f"📅 Date Range: {start_date} to {end_date}")
    print(f"📊 Minimum Edge: {min_edge*100:.1f}%")
    print(f"📈 Formula: (35% Averaged Models) + (65% Implied Odds)")
    print("=" * 100)
    print()
    
    # Load unified results
    df = pd.read_csv(unified_path)
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    
    # Filter date range
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    df = df[mask].copy()
    
    print(f"📊 Found {len(df)} games in date range\n")
    
    results = []
    
    for idx, row in df.iterrows():
        # Extract data
        date = row['date']
        favorite = row['favorite']
        underdog = row['underdog']
        spread = row['spread']
        fav_odds = row['fav_odds']
        dog_odds = row['dog_odds']
        actual_cover = row.get('actual_cover', np.nan)
        
        # Get model probabilities
        logistic_prob = row.get('logistic_fav_prob', np.nan)
        linear_prob = row.get('linear_fav_prob', np.nan)
        rf_prob = row.get('rf_fav_prob', np.nan)
        tree_prob = row.get('tree_fav_prob', np.nan)
        
        # Compute averaged pick
        pick_info = compute_averaged_pick(
            logistic_prob, linear_prob, rf_prob, tree_prob,
            fav_odds, dog_odds, min_edge
        )
        
        # Determine pick team
        if pick_info['pick_side'] == 'FAVORITE':
            pick_info['pick_team'] = favorite
        elif pick_info['pick_side'] == 'UNDERDOG':
            pick_info['pick_team'] = underdog
        
        # Evaluate result
        if pick_info['pick_side'] == 'NO BET':
            result = 'NO BET'
        elif pd.isna(actual_cover):
            result = 'PENDING'
        else:
            if pick_info['pick_side'] == 'FAVORITE':
                result = 'WIN' if actual_cover == 1 else 'LOSS'
            else:  # UNDERDOG
                result = 'WIN' if actual_cover == 0 else 'LOSS'
        
        # Store result
        results.append({
            'date': date,
            'favorite': favorite,
            'underdog': underdog,
            'spread': spread,
            'fav_odds': fav_odds,
            'dog_odds': dog_odds,
            'logistic_prob': logistic_prob,
            'linear_prob': linear_prob,
            'rf_prob': rf_prob,
            'tree_prob': tree_prob,
            **pick_info,
            'actual_cover': actual_cover,
            'result': result
        })
    
    return pd.DataFrame(results)


def analyze_results(df: pd.DataFrame):
    """Analyze and display results."""
    
    print("\n" + "=" * 100)
    print("📊 BACKTEST RESULTS")
    print("=" * 100)
    
    # Filter to completed games
    completed = df[df['result'].isin(['WIN', 'LOSS', 'PUSH', 'NO BET'])].copy()
    picks = completed[completed['pick_side'] != 'NO BET'].copy()
    no_bets = completed[completed['pick_side'] == 'NO BET']
    
    print(f"\n📈 OVERALL STATISTICS")
    print(f"   Total Games: {len(completed)}")
    print(f"   Games with Pick: {len(picks)}")
    print(f"   No Bets (edge < 3%): {len(no_bets)}")
    if len(completed) > 0:
        print(f"   Pick Rate: {len(picks)/len(completed)*100:.1f}%")
    
    if len(picks) == 0:
        print("\n⚠️ No picks made")
        return
    
    # Win/Loss breakdown
    wins = len(picks[picks['result'] == 'WIN'])
    losses = len(picks[picks['result'] == 'LOSS'])
    pushes = len(picks[picks['result'] == 'PUSH'])
    
    if wins + losses > 0:
        win_rate = wins / (wins + losses) * 100
    else:
        win_rate = 0
    
    print(f"\n🏆 PERFORMANCE")
    print(f"   Record: {wins}-{losses}-{pushes}")
    print(f"   Win Rate: {win_rate:.2f}%")
    
    # Betting performance
    if wins + losses > 0:
        # Flat betting ($100 per pick)
        profit_flat = (wins * 90.91) - (losses * 100)  # Assuming -110 juice
        roi_flat = (profit_flat / ((wins + losses) * 100)) * 100
        
        print(f"\n💰 BETTING PERFORMANCE (Flat $100)")
        print(f"   Total Wagered: ${(wins + losses) * 100:,.2f}")
        print(f"   Profit/Loss: ${profit_flat:,.2f}")
        print(f"   ROI: {roi_flat:.2f}%")
    
    # Breakdown by side
    fav_picks = picks[picks['pick_side'] == 'FAVORITE']
    dog_picks = picks[picks['pick_side'] == 'UNDERDOG']
    
    print(f"\n📊 PICK BREAKDOWN")
    if len(fav_picks) > 0:
        fav_wins = len(fav_picks[fav_picks['result'] == 'WIN'])
        fav_total = len(fav_picks[fav_picks['result'].isin(['WIN', 'LOSS'])])
        if fav_total > 0:
            print(f"   Favorites: {fav_wins}-{fav_total-fav_wins} ({fav_wins/fav_total*100:.1f}%)")
    
    if len(dog_picks) > 0:
        dog_wins = len(dog_picks[dog_picks['result'] == 'WIN'])
        dog_total = len(dog_picks[dog_picks['result'].isin(['WIN', 'LOSS'])])
        if dog_total > 0:
            print(f"   Underdogs: {dog_wins}-{dog_total-dog_wins} ({dog_wins/dog_total*100:.1f}%)")
    
    # Edge distribution of picks
    print(f"\n📈 EDGE DISTRIBUTION")
    print(f"   Min Edge: {picks['edge'].min():.1%}")
    print(f"   Max Edge: {picks['edge'].max():.1%}")
    print(f"   Avg Edge: {picks['edge'].mean():.1%}")
    
    # Performance by edge range
    print(f"\n🎯 PERFORMANCE BY EDGE")
    edge_ranges = [
        (0.03, 0.05, "3-5%"),
        (0.05, 0.08, "5-8%"),
        (0.08, 0.15, "8-15%"),
        (0.15, 1.00, "15%+")
    ]
    
    for min_e, max_e, label in edge_ranges:
        range_picks = picks[(picks['edge'] >= min_e) & (picks['edge'] < max_e)]
        range_picks = range_picks[range_picks['result'].isin(['WIN', 'LOSS'])]
        if len(range_picks) > 0:
            range_wins = len(range_picks[range_picks['result'] == 'WIN'])
            print(f"   {label}: {range_wins}-{len(range_picks)-range_wins} ({range_wins/len(range_picks)*100:.1f}%)")
    
    print("\n" + "=" * 100)


def main():
    parser = argparse.ArgumentParser(description='Backtest Standardized & Averaged Model')
    parser.add_argument('--start-date', type=str, default='2025-10-23',
                       help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, default='2025-12-18',
                       help='End date (YYYY-MM-DD)')
    parser.add_argument('--min-edge', type=float, default=0.03,
                       help='Minimum edge threshold (default: 0.03 = 3%%)')
    parser.add_argument('--output', type=str, default='data/averaged_model_backtest.csv',
                       help='Output CSV path')
    parser.add_argument('--history', type=str, default='data/averaged_model_predictions_history.csv',
                       help='Historical archive path')
    
    args = parser.parse_args()
    
    # Run backtest
    results_df = backtest(
        start_date=args.start_date,
        end_date=args.end_date,
        min_edge=args.min_edge
    )
    
    # Save current snapshot (overwrite)
    results_df.to_csv(args.output, index=False)
    print(f"\n💾 Results saved to: {args.output}")
    
    # Update historical archive (append new predictions only)
    import os
    if os.path.exists(args.history):
        # Load existing history
        history_df = pd.read_csv(args.history)
        history_df['date'] = pd.to_datetime(history_df['date']).dt.strftime('%Y-%m-%d')
        
        # Find new predictions (not in history)
        new_predictions = results_df[~results_df['date'].isin(history_df['date'])].copy()
        
        if len(new_predictions) > 0:
            # Append new predictions
            updated_history = pd.concat([history_df, new_predictions], ignore_index=True)
            updated_history = updated_history.sort_values('date').reset_index(drop=True)
            updated_history.to_csv(args.history, index=False)
            print(f"📚 Added {len(new_predictions)} new predictions to history: {args.history}")
        else:
            print(f"📚 No new predictions to add to history")
    else:
        # Create new history file
        results_df.to_csv(args.history, index=False)
        print(f"📚 Created historical archive: {args.history}")
    
    # Analyze
    analyze_results(results_df)


if __name__ == "__main__":
    main()
