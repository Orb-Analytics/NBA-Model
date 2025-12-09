"""
NBA Spread Prediction - Model Performance Analysis
Author: Orb Analytics (Liam Chaitin)
Purpose: Analyze and compare all model performances
"""

import pandas as pd
import numpy as np

def analyze_ensemble_results():
    """Comprehensive analysis of all models."""
    
    # Load results
    df = pd.read_csv('data/ensemble_model_results.csv')
    
    print("\n" + "="*100)
    print("📊 ENSEMBLE MODEL PERFORMANCE ANALYSIS")
    print("="*100)
    
    # Overall summary
    print("\n1️⃣  OVERALL ACCURACY BY MODEL")
    print("-" * 100)
    print(f"{'Model':<20} {'Accuracy':<12} {'Correct':<10} {'Total':<10} {'Avg Probability':<20}")
    print("-" * 100)
    
    model_stats = []
    for model_name in ['logistic', 'linear', 'random_forest', 'decision_tree']:
        model_df = df[df['model_name'] == model_name]
        accuracy = model_df['correct'].mean() * 100
        correct = model_df['correct'].sum()
        total = len(model_df)
        avg_prob = model_df['probability'].mean() * 100
        
        model_stats.append({
            'model': model_name,
            'accuracy': accuracy,
            'correct': correct,
            'total': total
        })
        
        print(f"{model_name.replace('_', ' ').title():<20} {accuracy:>6.2f}%{'':<4} {correct:>4}/{total:<5} {avg_prob:>6.2f}%")
    
    # Home vs Away breakdown
    print("\n2️⃣  HOME VS AWAY FAVORITE ACCURACY")
    print("-" * 100)
    print(f"{'Model':<20} {'Home Fav Acc':<15} {'Home Record':<15} {'Away Fav Acc':<15} {'Away Record'}")
    print("-" * 100)
    
    for model_name in ['logistic', 'linear', 'random_forest', 'decision_tree']:
        model_df = df[df['model_name'] == model_name]
        
        home_df = model_df[model_df['model_type'] == 'Home Favorite']
        away_df = model_df[model_df['model_type'] == 'Away Favorite']
        
        home_acc = home_df['correct'].mean() * 100 if len(home_df) > 0 else 0
        away_acc = away_df['correct'].mean() * 100 if len(away_df) > 0 else 0
        
        home_record = f"{home_df['correct'].sum()}/{len(home_df)}" if len(home_df) > 0 else "N/A"
        away_record = f"{away_df['correct'].sum()}/{len(away_df)}" if len(away_df) > 0 else "N/A"
        
        print(f"{model_name.replace('_', ' ').title():<20} {home_acc:>6.2f}%{'':<8} {home_record:<15} {away_acc:>6.2f}%{'':<8} {away_record}")
    
    # Consensus analysis
    print("\n3️⃣  CONSENSUS PREDICTIONS")
    print("-" * 100)
    
    # Group by date and game
    game_groups = df.groupby(['date', 'favorite', 'underdog'])
    
    consensus_results = []
    for (date, fav, dog), group in game_groups:
        # Get predictions from all 4 models
        votes_cover = (group['predicted_cover'] == 1).sum()
        actual_cover = group.iloc[0]['actual_cover']
        
        # Consensus is majority vote
        consensus_pred = 1 if votes_cover >= 3 else 0
        consensus_correct = consensus_pred == actual_cover
        
        consensus_results.append({
            'date': date,
            'votes_cover': votes_cover,
            'consensus_pred': consensus_pred,
            'actual_cover': actual_cover,
            'correct': consensus_correct,
            'model_type': group.iloc[0]['model_type']
        })
    
    consensus_df = pd.DataFrame(consensus_results)
    
    print(f"Total Games: {len(consensus_df)}")
    print(f"Consensus Accuracy: {consensus_df['correct'].mean() * 100:.2f}% ({consensus_df['correct'].sum()}/{len(consensus_df)})")
    
    # By confidence level
    print("\n   By Confidence Level:")
    for votes in [4, 3, 2, 1, 0]:
        vote_df = consensus_df[
            ((consensus_df['votes_cover'] == votes) & (consensus_df['consensus_pred'] == 1)) |
            ((consensus_df['votes_cover'] == 4 - votes) & (consensus_df['consensus_pred'] == 0))
        ]
        
        if len(vote_df) > 0:
            acc = vote_df['correct'].mean() * 100
            confidence = max(votes, 4 - votes)
            print(f"   {confidence}/4 Models Agree: {acc:>6.2f}% ({vote_df['correct'].sum()}/{len(vote_df)} games)")
    
    # By model type for consensus
    print("\n   By Model Type:")
    home_consensus = consensus_df[consensus_df['model_type'] == 'Home Favorite']
    away_consensus = consensus_df[consensus_df['model_type'] == 'Away Favorite']
    
    print(f"   🏠 Home Favorite: {home_consensus['correct'].mean() * 100:.2f}% ({home_consensus['correct'].sum()}/{len(home_consensus)})")
    print(f"   ✈️  Away Favorite: {away_consensus['correct'].mean() * 100:.2f}% ({away_consensus['correct'].sum()}/{len(away_consensus)})")
    
    # Model agreement analysis
    print("\n4️⃣  MODEL AGREEMENT ANALYSIS")
    print("-" * 100)
    
    agreement_analysis = []
    for (date, fav, dog), group in game_groups:
        predictions = group['predicted_cover'].values
        votes_cover = (predictions == 1).sum()
        actual = group.iloc[0]['actual_cover']
        
        # Check outcomes by agreement level
        if votes_cover == 4 or votes_cover == 0:
            agreement = "unanimous"
        elif votes_cover == 3 or votes_cover == 1:
            agreement = "strong"
        else:
            agreement = "split"
        
        majority_pred = 1 if votes_cover >= 3 else 0
        correct = majority_pred == actual
        
        agreement_analysis.append({
            'agreement': agreement,
            'correct': correct
        })
    
    agreement_df = pd.DataFrame(agreement_analysis)
    
    for agreement_type in ['unanimous', 'strong', 'split']:
        subset = agreement_df[agreement_df['agreement'] == agreement_type]
        if len(subset) > 0:
            acc = subset['correct'].mean() * 100
            print(f"{agreement_type.title():<15} {acc:>6.2f}% ({subset['correct'].sum()}/{len(subset)} games)")
    
    # Best model combination
    print("\n5️⃣  BEST MODEL COMBINATIONS")
    print("-" * 100)
    
    from itertools import combinations
    
    model_names = ['logistic', 'linear', 'random_forest', 'decision_tree']
    combo_results = []
    
    for r in range(1, 5):
        for combo in combinations(model_names, r):
            combo_predictions = []
            
            for (date, fav, dog), group in game_groups:
                combo_group = group[group['model_name'].isin(combo)]
                votes = (combo_group['predicted_cover'] == 1).sum()
                total = len(combo_group)
                
                # Majority vote
                pred = 1 if votes > total / 2 else 0
                actual = group.iloc[0]['actual_cover']
                
                combo_predictions.append({
                    'correct': pred == actual
                })
            
            combo_df = pd.DataFrame(combo_predictions)
            accuracy = combo_df['correct'].mean() * 100
            
            combo_results.append({
                'models': ' + '.join([m.replace('_', ' ').title() for m in combo]),
                'size': len(combo),
                'accuracy': accuracy,
                'correct': combo_df['correct'].sum(),
                'total': len(combo_df)
            })
    
    # Sort by accuracy
    combo_results_df = pd.DataFrame(combo_results)
    combo_results_df = combo_results_df.sort_values('accuracy', ascending=False)
    
    print("\nTop 10 Combinations:")
    print(f"{'Models':<60} {'Accuracy':<12} {'Record'}")
    print("-" * 100)
    for idx, row in combo_results_df.head(10).iterrows():
        print(f"{row['models']:<60} {row['accuracy']:>6.2f}%{'':<4} {row['correct']}/{row['total']}")
    
    print("\n" + "="*100)
    
    return {
        'model_stats': model_stats,
        'consensus_df': consensus_df,
        'agreement_df': agreement_df,
        'combo_results': combo_results_df
    }


def main():
    """Run comprehensive analysis."""
    results = analyze_ensemble_results()
    print("\n✅ Analysis complete")


if __name__ == "__main__":
    main()
