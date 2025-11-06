"""
Analysis and Visualization of Daily NBA Spread Predictions
Author: Orb Analytics (Liam Chaitin)
Purpose: Analyze performance of rolling daily predictions
"""

import pandas as pd
import numpy as np
from datetime import datetime

def analyze_results(results_path='./data/daily_predictions_results.csv'):
    """Analyze and print comprehensive results."""
    
    df = pd.read_csv(results_path)
    
    # Filter to only predictions with actual results
    df_completed = df[df['actual_cover'].notna()].copy()
    
    print("="*80)
    print("📊 COMPREHENSIVE PERFORMANCE ANALYSIS")
    print("="*80)
    print(f"\nData: {results_path}")
    print(f"Total Predictions: {len(df)}")
    print(f"Completed Games: {len(df_completed)}")
    print(f"Pending Predictions: {len(df) - len(df_completed)}")
    
    if len(df_completed) == 0:
        print("\n⚠️  No completed games to analyze yet")
        return
    
    # Overall Performance
    print("\n" + "="*80)
    print("🎯 OVERALL PERFORMANCE")
    print("="*80)
    overall_accuracy = df_completed['correct'].mean()
    print(f"Accuracy: {overall_accuracy:.2%} ({df_completed['correct'].sum()}/{len(df_completed)})")
    print(f"Average Confidence: {df_completed['cover_probability'].mean():.2%}")
    
    # Model Breakdown
    print("\n" + "="*80)
    print("🏠 PERFORMANCE BY MODEL TYPE")
    print("="*80)
    
    for model in ['Home Favorite', 'Away Favorite']:
        model_df = df_completed[df_completed['model'] == model]
        if len(model_df) > 0:
            acc = model_df['correct'].mean()
            print(f"\n{model}:")
            print(f"  Games: {len(model_df)}")
            print(f"  Accuracy: {acc:.2%} ({model_df['correct'].sum()}/{len(model_df)})")
            print(f"  Avg Confidence: {model_df['cover_probability'].mean():.2%}")
    
    # Confidence Buckets
    print("\n" + "="*80)
    print("📈 PERFORMANCE BY CONFIDENCE LEVEL")
    print("="*80)
    
    confidence_buckets = [
        ("Very High (>80% or <20%)", (df_completed['cover_probability'] >= 0.8) | (df_completed['cover_probability'] <= 0.2)),
        ("High (60-80% or 20-40%)", ((df_completed['cover_probability'] >= 0.6) & (df_completed['cover_probability'] < 0.8)) | 
                                    ((df_completed['cover_probability'] > 0.2) & (df_completed['cover_probability'] <= 0.4))),
        ("Medium (50-60% or 40-50%)", ((df_completed['cover_probability'] >= 0.5) & (df_completed['cover_probability'] < 0.6)) | 
                                      ((df_completed['cover_probability'] > 0.4) & (df_completed['cover_probability'] <= 0.5)))
    ]
    
    for label, mask in confidence_buckets:
        bucket_df = df_completed[mask]
        if len(bucket_df) > 0:
            acc = bucket_df['correct'].mean()
            print(f"\n{label}:")
            print(f"  Games: {len(bucket_df)}")
            print(f"  Accuracy: {acc:.2%} ({bucket_df['correct'].sum()}/{len(bucket_df)})")
    
    # Daily Performance
    print("\n" + "="*80)
    print("📅 DAILY PERFORMANCE")
    print("="*80)
    
    daily_stats = df_completed.groupby('date').agg({
        'correct': ['count', 'sum', 'mean']
    }).round(3)
    daily_stats.columns = ['Games', 'Correct', 'Accuracy']
    daily_stats['Accuracy'] = daily_stats['Accuracy'].apply(lambda x: f"{x:.1%}")
    
    print(daily_stats.to_string())
    
    # Best and Worst Days
    print("\n" + "="*80)
    print("🏆 BEST & WORST DAYS")
    print("="*80)
    
    daily_accuracy = df_completed.groupby('date').apply(lambda x: x['correct'].mean())
    best_days = daily_accuracy.nlargest(3)
    worst_days = daily_accuracy.nsmallest(3)
    
    print("\n✨ Best Days:")
    for date, acc in best_days.items():
        games_that_day = df_completed[df_completed['date'] == date]
        print(f"  {date}: {acc:.1%} ({games_that_day['correct'].sum()}/{len(games_that_day)} correct)")
    
    print("\n💔 Worst Days:")
    for date, acc in worst_days.items():
        games_that_day = df_completed[df_completed['date'] == date]
        print(f"  {date}: {acc:.1%} ({games_that_day['correct'].sum()}/{len(games_that_day)} correct)")
    
    # Betting Simulation
    print("\n" + "="*80)
    print("💰 BETTING SIMULATION")
    print("="*80)
    
    # Flat betting (bet $100 on every game)
    df_completed['bet_result_flat'] = df_completed['correct'].apply(lambda x: 100 if x else -110)
    flat_profit = df_completed['bet_result_flat'].sum()
    flat_roi = (flat_profit / (len(df_completed) * 110)) * 100
    
    print(f"\nFlat Betting (bet $100 on every game):")
    print(f"  Total Bets: {len(df_completed)}")
    print(f"  Total Profit: ${flat_profit:,.2f}")
    print(f"  ROI: {flat_roi:.2f}%")
    
    # High confidence only
    high_conf_mask = (df_completed['cover_probability'] >= 0.7) | (df_completed['cover_probability'] <= 0.3)
    df_high_conf = df_completed[high_conf_mask]
    
    if len(df_high_conf) > 0:
        high_conf_profit = df_high_conf['bet_result_flat'].sum()
        high_conf_roi = (high_conf_profit / (len(df_high_conf) * 110)) * 100
        
        print(f"\nHigh Confidence Only (>70% or <30%):")
        print(f"  Total Bets: {len(df_high_conf)}")
        print(f"  Correct: {df_high_conf['correct'].sum()} ({df_high_conf['correct'].mean():.1%})")
        print(f"  Total Profit: ${high_conf_profit:,.2f}")
        print(f"  ROI: {high_conf_roi:.2f}%")
    
    # Kelly Criterion simulation (simplified)
    df_completed['kelly_bet'] = df_completed.apply(
        lambda row: max(0, (row['cover_probability'] - 0.5) * 2 * 100) if row['cover_probability'] > 0.5 
        else max(0, (0.5 - row['cover_probability']) * 2 * 100), 
        axis=1
    )
    df_completed['kelly_result'] = df_completed.apply(
        lambda row: row['kelly_bet'] if row['correct'] else -row['kelly_bet'] * 1.1,
        axis=1
    )
    kelly_profit = df_completed['kelly_result'].sum()
    kelly_total_risked = df_completed['kelly_bet'].sum()
    kelly_roi = (kelly_profit / kelly_total_risked * 100) if kelly_total_risked > 0 else 0
    
    print(f"\nKelly Criterion (proportional to confidence):")
    print(f"  Total Risked: ${kelly_total_risked:,.2f}")
    print(f"  Total Profit: ${kelly_profit:,.2f}")
    print(f"  ROI: {kelly_roi:.2f}%")
    
    # Pending Predictions
    if len(df) > len(df_completed):
        print("\n" + "="*80)
        print("⏳ PENDING PREDICTIONS (Nov 5, 2025)")
        print("="*80)
        
        df_pending = df[df['actual_cover'].isna()].copy()
        print(f"\nTotal: {len(df_pending)} games")
        
        for idx, row in df_pending.iterrows():
            pred_text = "COVER" if row['predicted_cover'] == 1 else "NO COVER"
            conf_emoji = "💪" if row['cover_probability'] >= 0.7 or row['cover_probability'] <= 0.3 else "⚖️"
            
            print(f"\n{conf_emoji} {row['favorite']} vs {row['underdog']} (Spread: {row['spread']})")
            print(f"   Prediction: Favorite will {pred_text}")
            print(f"   Confidence: {row['cover_probability']:.1%}")
            print(f"   Model: {row['model']}")
    
    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE")
    print("="*80)


if __name__ == "__main__":
    analyze_results()
