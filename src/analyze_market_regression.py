"""
NBA Spread Prediction - Market Regression Analysis
Author: Orb Analytics (Liam Chaitin)
Purpose: Test regressing model predictions toward market odds (35% model, 65% implied prob)
         Then calculate predictive edge from regressed probability
"""

import pandas as pd
import numpy as np

def american_odds_to_probability(odds):
    """Convert American odds to implied probability."""
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)
    else:
        return 100 / (odds + 100)

def analyze_market_regression(model_name):
    """
    Analyze model performance with market regression.
    
    Regressed Probability = 0.35 * Model Prob + 0.65 * Implied Prob
    Predictive Edge = Regressed Prob - Implied Prob
    """
    print(f"\n{'='*90}")
    print(f"📊 MARKET REGRESSION ANALYSIS: {model_name.upper().replace('_', ' ')}")
    print(f"{'='*90}")
    
    # Load model results
    model_df = pd.read_csv(f'data/{model_name}_model_results.csv')
    
    # Load training data to get odds
    training_df = pd.read_csv('data/NBA Training Set 25-26.csv')
    training_df['Date'] = pd.to_datetime(training_df['Date']).dt.strftime('%Y-%m-%d')
    
    # Merge to get odds data
    merged = model_df.merge(
        training_df[['Date', 'Favorite', 'Underdog', 'Fav. Odds', 'Dog Odds']],
        left_on=['date', 'favorite', 'underdog'],
        right_on=['Date', 'Favorite', 'Underdog'],
        how='left'
    )
    
    # Filter for games with odds data
    merged = merged[merged['Fav. Odds'].notna()].copy()
    
    if len(merged) == 0:
        print("⚠️ No games with odds data found")
        return None
    
    # Calculate implied probabilities
    merged['fav_implied_prob'] = merged['Fav. Odds'].apply(american_odds_to_probability)
    merged['dog_implied_prob'] = merged['Dog Odds'].apply(american_odds_to_probability)
    
    # Model probabilities (already in the data)
    merged['model_fav_prob'] = merged['probability']
    merged['model_dog_prob'] = 1 - merged['probability']
    
    # MARKET REGRESSION: 35% model, 65% market
    merged['regressed_fav_prob'] = 0.35 * merged['model_fav_prob'] + 0.65 * merged['fav_implied_prob']
    merged['regressed_dog_prob'] = 0.35 * merged['model_dog_prob'] + 0.65 * merged['dog_implied_prob']
    
    # Calculate predictive edges from REGRESSED probabilities
    merged['fav_predictive_edge'] = merged['regressed_fav_prob'] - merged['fav_implied_prob']
    merged['dog_predictive_edge'] = merged['regressed_dog_prob'] - merged['dog_implied_prob']
    
    # Determine best bet based on regressed edge
    merged['best_edge'] = merged[['fav_predictive_edge', 'dog_predictive_edge']].max(axis=1)
    merged['best_side'] = merged.apply(
        lambda x: 'favorite' if x['fav_predictive_edge'] > x['dog_predictive_edge'] else 'underdog',
        axis=1
    )
    
    # Make prediction based on regressed probability
    merged['regressed_prediction'] = (merged['regressed_fav_prob'] > 0.5).astype(int)
    merged['regressed_correct'] = (merged['regressed_prediction'] == merged['actual_cover']).astype(int)
    
    # ORIGINAL model performance (no regression)
    original_accuracy = merged['correct'].mean() * 100
    original_correct = merged['correct'].sum()
    
    # REGRESSED model performance
    regressed_accuracy = merged['regressed_correct'].mean() * 100
    regressed_correct = merged['regressed_correct'].sum()
    
    total_games = len(merged)
    
    print(f"\n📈 OVERALL PERFORMANCE COMPARISON")
    print(f"{'='*90}")
    print(f"Total Games: {total_games}")
    print()
    print(f"{'Method':<30} {'Accuracy':<15} {'Record':<15} {'Improvement'}")
    print(f"{'-'*90}")
    print(f"{'Original Model':<30} {original_accuracy:>6.2f}%{'':<7} {original_correct:>3}/{total_games:<10}")
    print(f"{'Market Regression (35/65)':<30} {regressed_accuracy:>6.2f}%{'':<7} {regressed_correct:>3}/{total_games:<10} {regressed_accuracy - original_accuracy:+.2f}%")
    
    # By model type
    print(f"\n📍 BY SCENARIO")
    print(f"{'='*90}")
    
    for scenario in ['Home Favorite', 'Away Favorite']:
        scenario_df = merged[merged['model_type'] == scenario]
        
        if len(scenario_df) > 0:
            orig_acc = scenario_df['correct'].mean() * 100
            reg_acc = scenario_df['regressed_correct'].mean() * 100
            
            icon = "🏠" if scenario == "Home Favorite" else "✈️ "
            print(f"\n{icon} {scenario.upper()}")
            print(f"{'Method':<30} {'Accuracy':<15} {'Record':<15} {'Improvement'}")
            print(f"{'-'*90}")
            print(f"{'Original':<30} {orig_acc:>6.2f}%{'':<7} {scenario_df['correct'].sum():>3}/{len(scenario_df):<10}")
            print(f"{'Regressed (35/65)':<30} {reg_acc:>6.2f}%{'':<7} {scenario_df['regressed_correct'].sum():>3}/{len(scenario_df):<10} {reg_acc - orig_acc:+.2f}%")
    
    # Betting strategy: Only bet when edge > threshold
    print(f"\n🎯 BETTING WITH PREDICTIVE EDGE (Regressed)")
    print(f"{'='*90}")
    
    edge_thresholds = [0.00, 0.02, 0.05, 0.10]
    
    print(f"{'Edge Threshold':<20} {'Bets':<10} {'Win Rate':<15} {'Record':<15} {'ROI (est)'}")
    print(f"{'-'*90}")
    
    for threshold in edge_thresholds:
        # Filter for positive edge above threshold
        edge_bets = merged[merged['best_edge'] > threshold].copy()
        
        if len(edge_bets) > 0:
            # Check if the bet was correct
            edge_bets['bet_correct'] = edge_bets.apply(
                lambda x: (x['best_side'] == 'favorite' and x['actual_cover'] == 1) or 
                         (x['best_side'] == 'underdog' and x['actual_cover'] == 0),
                axis=1
            )
            
            win_rate = edge_bets['bet_correct'].mean() * 100
            wins = edge_bets['bet_correct'].sum()
            total_bets = len(edge_bets)
            
            # Estimate ROI (assuming -110 odds, need 52.38% to break even)
            # Win: +0.909 units, Loss: -1 unit
            roi = ((wins * 0.909) - ((total_bets - wins) * 1.0)) / total_bets * 100 if total_bets > 0 else 0
            
            print(f">{threshold*100:.0f}%{'':<15} {total_bets:<10} {win_rate:>6.2f}%{'':<7} {wins:>3}/{total_bets:<10} {roi:+.2f}%")
        else:
            print(f">{threshold*100:.0f}%{'':<15} {'0':<10} {'N/A':<15} {'0/0':<15} {'N/A'}")
    
    # Save detailed results
    output_file = f'data/{model_name}_market_regression.csv'
    merged.to_csv(output_file, index=False)
    print(f"\n💾 Detailed results saved to {output_file}")
    
    print(f"{'='*90}\n")
    
    return {
        'model': model_name,
        'original_accuracy': original_accuracy,
        'regressed_accuracy': regressed_accuracy,
        'improvement': regressed_accuracy - original_accuracy,
        'total_games': total_games
    }


def main():
    """Run market regression analysis for all models."""
    import sys
    
    models = ['logistic', 'linear', 'random_forest', 'decision_tree']
    
    if len(sys.argv) > 1:
        # Analyze specific model
        model_name = sys.argv[1].lower()
        if model_name in models:
            analyze_market_regression(model_name)
        else:
            print(f"❌ Invalid model name: {model_name}")
            print(f"Valid options: {', '.join(models)}")
    else:
        # Analyze all models
        all_results = []
        
        for model_name in models:
            result = analyze_market_regression(model_name)
            if result:
                all_results.append(result)
        
        # Summary comparison
        if all_results:
            print(f"\n{'='*90}")
            print("📊 MARKET REGRESSION SUMMARY - ALL MODELS")
            print(f"{'='*90}\n")
            
            print(f"{'Model':<20} {'Original Acc':<15} {'Regressed Acc':<15} {'Improvement':<15} {'Games'}")
            print(f"{'-'*90}")
            
            for result in all_results:
                print(f"{result['model'].replace('_', ' ').title():<20} "
                      f"{result['original_accuracy']:>6.2f}%{'':<7} "
                      f"{result['regressed_accuracy']:>6.2f}%{'':<7} "
                      f"{result['improvement']:>+6.2f}%{'':<7} "
                      f"{result['total_games']}")
            
            print(f"{'='*90}")
            print("\n✅ Market regression analysis complete")


if __name__ == "__main__":
    main()
