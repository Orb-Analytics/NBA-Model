"""
NBA Spread Prediction - Unified Model Backtesting
Author: Orb Analytics (Liam Chaitin)
Purpose: Run all four models with dynamic feature selection and output comprehensive results
         Starting from 2025-10-22 (beginning of season)
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import existing model classes
from logistic_spread_model import LogisticSpreadModel
from linear_spread_model import LinearSpreadModel
from random_forest_spread_model import RandomForestSpreadModel
from decision_tree_spread_model import DecisionTreeSpreadModel


def run_unified_backtest(start_date='2025-10-22', end_date='2025-11-21'):
    """
    Run all four models and combine results into a single CSV.
    Each model gets its own set of columns for comparison.
    """
    print(f"\n{'='*100}")
    print(f"🔬 UNIFIED MODEL BACKTESTING")
    print(f"{'='*100}")
    print(f"Period: {start_date} to {end_date}")
    print(f"Running 4 models with dynamic feature selection\n")
    
    # Initialize all models
    print("📂 Loading models...")
    logistic_model = LogisticSpreadModel('data/NBA Training Set 25-26.csv')
    linear_model = LinearSpreadModel('data/NBA Training Set 25-26.csv')
    rf_model = RandomForestSpreadModel('data/NBA Training Set 25-26.csv')
    tree_model = DecisionTreeSpreadModel('data/NBA Training Set 25-26.csv')
    
    logistic_model.load_data()
    linear_model.load_data()
    rf_model.load_data()
    tree_model.load_data()
    
    print("✅ All models loaded\n")
    
    # Collect results
    unified_results = []
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    total_games = 0
    for date in dates:
        date_str = date.strftime('%Y-%m-%d')
        
        # Train all models on data before this date
        logistic_model.train_models(date_str)
        linear_model.train_models(date_str)
        rf_model.train_models(date_str)
        tree_model.train_models(date_str)
        
        # Get games for this date
        games = logistic_model.df[logistic_model.df['Date'] == date_str]
        
        if len(games) == 0:
            continue
        
        print(f"📅 {date_str}: {len(games)} games")
        total_games += len(games)
        
        for idx, game in games.iterrows():
            # Skip if no actual result
            if pd.isna(game.get('Favorite Cover?')):
                continue
            
            # Get predictions from all models
            logistic_pred = logistic_model.predict_game(game)
            linear_pred = linear_model.predict_game(game)
            rf_pred = rf_model.predict_game(game)
            tree_pred = tree_model.predict_game(game)
            
            if not all([logistic_pred, linear_pred, rf_pred, tree_pred]):
                continue
            
            # Combine into single row
            result = {
                # Game info
                'date': date_str,
                'favorite': game['Favorite'],
                'underdog': game['Underdog'],
                'spread': game['Spread'],
                'fav_odds': logistic_pred['fav_odds'],
                'dog_odds': logistic_pred['dog_odds'],
                'fav_implied_prob': logistic_pred['fav_implied_prob'],
                'dog_implied_prob': logistic_pred['dog_implied_prob'],
                'actual_cover': logistic_pred['actual_cover'],
                'model_type': logistic_pred['model_type'],
                
                # Logistic model columns
                'logistic_fav_prob': logistic_pred['model_fav_probability'],
                'logistic_dog_prob': logistic_pred['model_dog_probability'],
                'logistic_fav_edge': logistic_pred['fav_predictive_edge'],
                'logistic_dog_edge': logistic_pred['dog_predictive_edge'],
                'logistic_best_edge': logistic_pred['best_edge'],
                'logistic_best_side': logistic_pred['best_side'],
                'logistic_predicted_cover': logistic_pred['predicted_cover'],
                'logistic_correct': int(logistic_pred['predicted_cover'] == logistic_pred['actual_cover']),
                
                # Linear model columns
                'linear_fav_prob': linear_pred['model_fav_probability'],
                'linear_dog_prob': linear_pred['model_dog_probability'],
                'linear_fav_edge': linear_pred['fav_predictive_edge'],
                'linear_dog_edge': linear_pred['dog_predictive_edge'],
                'linear_best_edge': linear_pred['best_edge'],
                'linear_best_side': linear_pred['best_side'],
                'linear_predicted_cover': linear_pred['predicted_cover'],
                'linear_correct': int(linear_pred['predicted_cover'] == linear_pred['actual_cover']),
                
                # Random Forest model columns
                'rf_fav_prob': rf_pred['model_fav_probability'],
                'rf_dog_prob': rf_pred['model_dog_probability'],
                'rf_fav_edge': rf_pred['fav_predictive_edge'],
                'rf_dog_edge': rf_pred['dog_predictive_edge'],
                'rf_best_edge': rf_pred['best_edge'],
                'rf_best_side': rf_pred['best_side'],
                'rf_predicted_cover': rf_pred['predicted_cover'],
                'rf_correct': int(rf_pred['predicted_cover'] == rf_pred['actual_cover']),
                
                # Decision Tree model columns
                'tree_fav_prob': tree_pred['model_fav_probability'],
                'tree_dog_prob': tree_pred['model_dog_probability'],
                'tree_fav_edge': tree_pred['fav_predictive_edge'],
                'tree_dog_edge': tree_pred['dog_predictive_edge'],
                'tree_best_edge': tree_pred['best_edge'],
                'tree_best_side': tree_pred['best_side'],
                'tree_predicted_cover': tree_pred['predicted_cover'],
                'tree_correct': int(tree_pred['predicted_cover'] == tree_pred['actual_cover']),
            }
            
            unified_results.append(result)
    
    # Create DataFrame
    results_df = pd.DataFrame(unified_results)
    
    print(f"\n{'='*100}")
    print(f"📊 BACKTESTING COMPLETE")
    print(f"{'='*100}")
    print(f"Total games analyzed: {len(results_df)}")
    print(f"Date range: {results_df['date'].min()} to {results_df['date'].max()}")
    
    # Print summary statistics
    print(f"\n📈 MODEL PERFORMANCE SUMMARY")
    print(f"{'-'*100}")
    print(f"{'Model':<20} {'Accuracy':<12} {'Record':<15} {'Home Fav':<15} {'Away Fav'}")
    print(f"{'-'*100}")
    
    for model_name, col_prefix in [('Logistic', 'logistic'), ('Linear', 'linear'), 
                                     ('Random Forest', 'rf'), ('Decision Tree', 'tree')]:
        accuracy = results_df[f'{col_prefix}_correct'].mean() * 100
        correct = results_df[f'{col_prefix}_correct'].sum()
        total = len(results_df)
        
        # By scenario
        home_df = results_df[results_df['model_type'] == 'Home Favorite']
        away_df = results_df[results_df['model_type'] == 'Away Favorite']
        
        home_acc = home_df[f'{col_prefix}_correct'].mean() * 100 if len(home_df) > 0 else 0
        away_acc = away_df[f'{col_prefix}_correct'].mean() * 100 if len(away_df) > 0 else 0
        
        print(f"{model_name:<20} {accuracy:>6.2f}%{'':<4} {correct:>3}/{total:<10} "
              f"{home_acc:>6.2f}%{'':<7} {away_acc:>6.2f}%")
    
    # Save results
    output_file = 'data/unified_model_results.csv'
    results_df.to_csv(output_file, index=False)
    print(f"\n💾 Results saved to {output_file}")
    print(f"   Columns: {len(results_df.columns)}")
    print(f"   Rows: {len(results_df)}")
    
    print(f"\n{'='*100}\n")
    
    return results_df


def main():
    """Run unified backtesting."""
    results = run_unified_backtest(start_date='2025-10-22', end_date='2025-11-21')
    print(f"✅ Unified backtesting complete!")
    print(f"   {len(results)} games analyzed across 4 models")


if __name__ == "__main__":
    main()
