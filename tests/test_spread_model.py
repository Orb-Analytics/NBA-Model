"""
Test and Demonstration Script for NBA Spread Prediction Model
Author: Orb Analytics (Liam Chaitin)
Purpose: Demonstrate model usage and make predictions on upcoming games
"""

import pandas as pd
import sys
sys.path.append('/workspaces/NBA-model/src')
from logistic_spread_model import SpreadPredictionModel


def test_model_on_historical_data():
    """Test the model on a subset of historical data."""
    print("="*80)
    print("📊 TESTING MODEL ON HISTORICAL DATA")
    print("="*80)
    
    # Initialize model
    data_path = '/workspaces/NBA-model/data/NBA Training Set 25-26.csv'
    model = SpreadPredictionModel(data_path)
    model.train_all()
    
    # Load test games (using last 20 games from dataset as example)
    df = pd.read_csv(data_path)
    df = df[df['Favorite Cover?'].notna()]
    test_games = df.tail(20).copy()
    
    print(f"\n🎯 Making predictions on {len(test_games)} recent games...")
    print("-"*80)
    
    # Make predictions
    predictions = model.predict(test_games)
    
    # Compare with actual results
    results = []
    for idx, (pred_idx, pred_row) in enumerate(predictions.iterrows()):
        actual_game = test_games.iloc[idx]
        actual_cover = actual_game['Favorite Cover?']
        predicted_cover = 1 if pred_row['Predicted_Cover'] == 'Yes' else 0
        
        correct = '✅' if actual_cover == predicted_cover else '❌'
        
        print(f"\nGame {idx+1}: {pred_row['Favorite']} vs {pred_row['Underdog']} (Spread: {pred_row['Spread']})")
        print(f"  Model Used: {pred_row['Model_Used']}")
        print(f"  Predicted: {pred_row['Predicted_Cover']} (Confidence: {pred_row['Cover_Probability']:.1%})")
        print(f"  Actual: {'Yes' if actual_cover == 1 else 'No'} {correct}")
        
        results.append({
            'correct': actual_cover == predicted_cover,
            'confidence': pred_row['Cover_Probability']
        })
    
    # Summary statistics
    accuracy = sum(r['correct'] for r in results) / len(results)
    avg_confidence = sum(r['confidence'] for r in results) / len(results)
    
    print("\n" + "="*80)
    print("📈 TEST RESULTS SUMMARY")
    print("="*80)
    print(f"Accuracy: {accuracy:.1%} ({sum(r['correct'] for r in results)}/{len(results)})")
    print(f"Average Confidence: {avg_confidence:.1%}")


def demonstrate_prediction_workflow():
    """Demonstrate how to use the model for new predictions."""
    print("\n\n")
    print("="*80)
    print("🔮 PREDICTION WORKFLOW DEMONSTRATION")
    print("="*80)
    print("\nThis example shows how to use the trained model to predict upcoming games.")
    print("You would replace the sample data below with actual game data.\n")
    
    # Load and train model
    data_path = '/workspaces/NBA-model/data/NBA Training Set 25-26.csv'
    model = SpreadPredictionModel(data_path)
    
    print("Step 1: Load and train the model")
    print("-"*80)
    model.train_all()
    
    print("\n\nStep 2: Prepare game data for prediction")
    print("-"*80)
    print("Format: DataFrame with all required features")
    
    # Example: Load a few games from the dataset as "new" games to predict
    df = pd.read_csv(data_path)
    df = df[df['Favorite Cover?'].notna()]
    
    # Take 5 games as examples (in real usage, these would be upcoming games)
    example_games = df.sample(5, random_state=42).copy()
    
    print(f"\nLoaded {len(example_games)} example games for prediction\n")
    
    print("Step 3: Make predictions")
    print("-"*80)
    predictions = model.predict(example_games)
    
    # Display predictions
    print("\n📋 PREDICTIONS:")
    for idx, row in predictions.iterrows():
        print(f"\n{idx+1}. {row['Favorite']} vs {row['Underdog']}")
        print(f"   Spread: {row['Spread']}")
        print(f"   Favorite at Home: {'Yes' if row['Fav_At_Home'] == 1 else 'No'}")
        print(f"   Model: {row['Model_Used']}")
        print(f"   🎯 Prediction: Favorite will {'COVER' if row['Predicted_Cover'] == 'Yes' else 'NOT COVER'}")
        print(f"   📊 Confidence: {row['Cover_Probability']:.1%}")
        
        # Betting recommendation
        if row['Cover_Probability'] >= 0.60:
            print(f"   💰 Recommendation: STRONG BET on Favorite to cover")
        elif row['Cover_Probability'] >= 0.55:
            print(f"   💵 Recommendation: Moderate bet on Favorite to cover")
        elif row['Cover_Probability'] <= 0.40:
            print(f"   💰 Recommendation: STRONG BET on Underdog to cover")
        elif row['Cover_Probability'] <= 0.45:
            print(f"   💵 Recommendation: Moderate bet on Underdog to cover")
        else:
            print(f"   ⚠️  Recommendation: SKIP - Too close to call")
    
    print("\n" + "="*80)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*80)


def main():
    """Run all tests and demonstrations."""
    # Test on historical data
    test_model_on_historical_data()
    
    # Demonstrate prediction workflow
    demonstrate_prediction_workflow()
    
    print("\n\n")
    print("="*80)
    print("📚 USAGE NOTES")
    print("="*80)
    print("""
To use this model in production:

1. Train the model periodically with updated data:
   ```python
   from src.logistic_spread_model import SpreadPredictionModel
   
   model = SpreadPredictionModel('/workspaces/NBA-model/data/NBA Training Set 25-26.csv')
   model.train_all()
   ```

2. Prepare upcoming game data with all required features

3. Make predictions:
   ```python
   predictions = model.predict(upcoming_games_df)
   ```

4. Use prediction confidence to guide betting decisions:
   - High confidence (>60%): Strong bet
   - Medium confidence (55-60%): Moderate bet
   - Low confidence (<55%): Skip or bet small

5. Track results and retrain model as new data becomes available

Key Features Selected:
- HOME FAVORITE MODEL: 15 features focused on recent form, rebounds, assists
- AWAY FAVORITE MODEL: 15 features emphasizing defensive stats and turnovers

Model Performance:
- HOME FAVORITE: ~60% cross-validated accuracy, 0.57 ROC AUC
- AWAY FAVORITE: ~60% cross-validated accuracy, 0.69 ROC AUC
    """)


if __name__ == "__main__":
    main()
