#!/usr/bin/env python3
"""
Rebuild averaged_model_predictions_history.csv from unified_model_results.csv

This script reconstructs the predictions history by:
1. Loading all games from unified_model_results.csv (has 3-model probabilities)
2. Calculating what the picks would have been using the averaged model formula
3. Saving all historical predictions to averaged_model_predictions_history.csv

Use this after major model changes (like removing Decision Tree) to restore full history.
"""

import pandas as pd
import numpy as np
import sys


def american_to_prob(odds: float) -> float:
    """Convert American odds to implied probability."""
    if pd.isna(odds):
        return np.nan
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return abs(odds) / (abs(odds) + 100)


def compute_averaged_pick(row, min_edge=0.03):
    """
    Compute the averaged & standardized pick from unified results row.
    
    Formula:
    - Average 3 model probabilities (Logistic, Linear, RF)
    - Standardized prob = (0.35 * averaged_model_prob) + (0.65 * implied_prob)
    - Edge = standardized_prob - implied_prob
    - Pick only if edge >= min_edge
    """
    # Get model probabilities
    logistic_prob = row.get('logistic_fav_prob', np.nan)
    linear_prob = row.get('linear_fav_prob', np.nan)
    rf_prob = row.get('rf_fav_prob', np.nan)
    
    # Count valid models
    probs = [logistic_prob, linear_prob, rf_prob]
    valid_probs = [p for p in probs if not pd.isna(p)]
    
    if len(valid_probs) == 0:
        return None
    
    # Average model probabilities
    averaged_fav_prob = np.mean(valid_probs)
    averaged_dog_prob = 1 - averaged_fav_prob
    
    # Get implied probabilities
    fav_implied = american_to_prob(row['fav_odds'])
    dog_implied = american_to_prob(row['dog_odds'])
    
    # Apply standardization formula
    standardized_fav = (0.35 * averaged_fav_prob) + (0.65 * fav_implied)
    standardized_dog = (0.35 * averaged_dog_prob) + (0.65 * dog_implied)
    
    # Calculate edges
    fav_edge = standardized_fav - fav_implied
    dog_edge = standardized_dog - dog_implied
    
    # Determine pick - only pick if we have a POSITIVE edge >= min_edge
    if fav_edge >= min_edge and fav_edge > dog_edge:
        pick_side = "FAVORITE"
        pick_team = row['favorite']
        edge = fav_edge
    elif dog_edge >= min_edge and dog_edge > fav_edge:
        pick_side = "UNDERDOG"
        pick_team = row['underdog']
        edge = dog_edge
    else:
        pick_side = "NO BET"
        pick_team = None
        edge = max(fav_edge, dog_edge) if not pd.isna(fav_edge) else 0.0
    
    # Determine result
    actual_cover = row.get('actual_cover', np.nan)
    if pick_side == 'NO BET':
        result = 'NO BET'
    elif pd.isna(actual_cover):
        result = 'PENDING'
    else:
        if pick_side == 'FAVORITE':
            result = 'WIN' if actual_cover == 1 else 'LOSS'
        else:  # UNDERDOG
            result = 'WIN' if actual_cover == 0 else 'LOSS'
    
    return {
        'date': row['date'],
        'favorite': row['favorite'],
        'underdog': row['underdog'],
        'spread': row['spread'],
        'fav_odds': row['fav_odds'],
        'dog_odds': row['dog_odds'],
        'logistic_prob': logistic_prob,
        'linear_prob': linear_prob,
        'rf_prob': rf_prob,
        'num_models': len(valid_probs),
        'averaged_fav_prob': averaged_fav_prob,
        'averaged_dog_prob': averaged_dog_prob,
        'standardized_fav': standardized_fav,
        'standardized_dog': standardized_dog,
        'fav_edge': fav_edge,
        'dog_edge': dog_edge,
        'pick_side': pick_side,
        'pick_team': pick_team,
        'edge': edge,
        'actual_cover': actual_cover,
        'result': result
    }


def rebuild_history(
    unified_path='data/unified_model_results.csv',
    output_path='data/averaged_model_predictions_history.csv',
    min_edge=0.03
):
    """
    Rebuild predictions history from unified model results.
    """
    print("=" * 100)
    print("🔄 REBUILDING PREDICTIONS HISTORY")
    print("=" * 100)
    print(f"📂 Source: {unified_path}")
    print(f"📂 Output: {output_path}")
    print(f"🎯 Min Edge: {min_edge*100:.1f}%")
    print("=" * 100)
    print()
    
    # Load unified results
    print("📊 Loading unified model results...")
    df = pd.read_csv(unified_path)
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    
    print(f"✅ Loaded {len(df)} games")
    print(f"📅 Date range: {df['date'].min()} to {df['date'].max()}")
    print()
    
    # Process each game
    print("🔄 Calculating picks for all games...")
    history_records = []
    
    for idx, row in df.iterrows():
        pick_info = compute_averaged_pick(row, min_edge)
        if pick_info:
            history_records.append(pick_info)
    
    # Create DataFrame
    history_df = pd.DataFrame(history_records)
    history_df = history_df.sort_values('date').reset_index(drop=True)
    
    # Save to file
    history_df.to_csv(output_path, index=False)
    
    print(f"✅ Saved {len(history_df)} games to {output_path}")
    print()
    
    # Show statistics
    picks = history_df[history_df['pick_side'] != 'NO BET']
    completed_picks = picks[picks['result'].isin(['WIN', 'LOSS'])]
    
    if len(completed_picks) > 0:
        wins = len(completed_picks[completed_picks['result'] == 'WIN'])
        losses = len(completed_picks[completed_picks['result'] == 'LOSS'])
        win_pct = wins / (wins + losses) * 100 if (wins + losses) > 0 else 0
        
        print("📊 STATISTICS:")
        print(f"   Total Games: {len(history_df)}")
        print(f"   Picks Made: {len(picks)}")
        print(f"   Pick Rate: {len(picks)/len(history_df)*100:.1f}%")
        print(f"   Completed Picks: {len(completed_picks)}")
        print(f"   Record: {wins}-{losses} ({win_pct:.1f}%)")
        print()
    
    print("=" * 100)
    print("✅ REBUILD COMPLETE")
    print("=" * 100)
    print()
    print("🔄 Next steps:")
    print("   1. Run: python src/backtest_averaged_simple.py")
    print("   2. Run: python src/update_backtest_results_md.py")
    print("   3. Commit the updated files")
    print("=" * 100)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Rebuild predictions history from unified results')
    parser.add_argument('--unified', type=str, default='data/unified_model_results.csv',
                       help='Path to unified model results CSV')
    parser.add_argument('--output', type=str, default='data/averaged_model_predictions_history.csv',
                       help='Output path for predictions history')
    parser.add_argument('--min-edge', type=float, default=0.03,
                       help='Minimum edge threshold (default: 0.03 = 3%%)')
    
    args = parser.parse_args()
    
    rebuild_history(
        unified_path=args.unified,
        output_path=args.output,
        min_edge=args.min_edge
    )


if __name__ == "__main__":
    main()
