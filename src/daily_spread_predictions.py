"""
NBA Daily Spread Prediction - Rolling Time Series Validation
Author: Orb Analytics (Liam Chaitin)
Purpose: Train model on historical data, predict each day's games, track performance
         Features are selected dynamically each day based on training data
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Feature sets for the two scenarios
HOME_PREDICTORS = [
    "Favorite PPG", "Underdog PPG", "Favorite PPG L3", "Underdog PPG L3", "Favorite PPG L1",
    "Underdog PPG L1", "Favorite PPG Home", "Underdog PPG Away", "Favorite PPGA", "Underdog PPGA",
    "Favorite PPGA L3", "Underdog PPGA L3", "Favorite PPGA L1", "Underdog PPGA L1", "Favorite PPGA Home",
    "Underdog PPGA Away", "Favorite Off. Efficiency", "Underdog Off. Efficiency",
    "Favorite Off. Efficiency L3", "Underdog Off. Efficiency L3", "Favorite Off. Efficiency L1",
    "Underdog Off. Efficiency L1", "Favorite Off. Efficiency Home", "Underdog Off. Efficiency Away",
    "Favorite Def. Efficiency", "Underdog Def. Efficiency", "Favorite Def. Efficiency L3",
    "Underdog Def. Efficiency L3", "Favorite Def. Efficiency L1", "Underdog Def. Efficiency L1",
    "Favorite Def. Efficiency Home", "Underdog Def. Efficiency Away", "Favorite Winning % in Close Games",
    "Underdog Winning % in Close Games", "Favorite Opp. Winning % in Close Games",
    "Underdog Opp. Winning % in Close Games", "Favorite 3 Pointers P/G", "Underdog 3 Pointers P/G",
    "Favorite 3 Pointers P/G L3", "Underdog 3 Pointers P/G L3", "Favorite 3 Pointers P/G L1",
    "Underdog 3 Pointers P/G L1", "Favorite 3 Pointers P/G Home", "Underdog 3 Pointers P/G Away",
    "Favorite Opp. 3 Pointers P/G", "Underdog Opp. 3 Pointers P/G", "Favorite Opp. 3 Pointers P/G L3",
    "Underdog Opp. 3 Pointers P/G L3", "Favorite Opp. 3 Pointers P/G L1", "Underdog Opp. 3 Pointers P/G L1",
    "Favorite Opp. 3 Pointers P/G Home", "Underdog Opp. 3 Pointers P/G Away", "Favorite Off. Rebounds P/G",
    "Underdog Off. Rebounds P/G", "Favorite Off. Rebounds P/G L3", "Underdog Off. Rebounds P/G L3",
    "Favorite Off. Rebounds P/G L1", "Underdog Off. Rebounds P/G L1", "Favorite Off. Rebounds P/G Home",
    "Underdog Off. Rebounds P/G Away", "Favorite Def. Rebounds P/G", "Underdog Def. Rebounds P/G",
    "Favorite Def. Rebounds P/G L3", "Underdog Def. Rebounds P/G L3", "Favorite Def. Rebounds P/G L1",
    "Underdog Def. Rebounds P/G L1", "Favorite Def. Rebounds P/G Home", "Underdog Def. Rebounds P/G Away",
    "Favorite Total Rebound %", "Underdog Total Rebound %", "Favorite Total Rebound % L3",
    "Underdog Total Rebound % L3", "Favorite Total Rebound % L1", "Underdog Total Rebound % L1",
    "Favorite Total Rebound % Home", "Underdog Total Rebound % Away", "Favorite Blocks P/G",
    "Underdog Blocks P/G", "Favorite Blocks P/G L3", "Underdog Blocks P/G L3", "Favorite Blocks P/G L1",
    "Underdog Blocks P/G L1", "Favorite Blocks P/G Home", "Underdog Blocks P/G Away",
    "Favorite Opp. Blocks P/G", "Underdog Opp. Blocks P/G", "Favorite Opp. Blocks P/G L3",
    "Underdog Opp. Blocks P/G L3", "Favorite Opp. Blocks P/G L1", "Underdog Opp. Blocks P/G L1",
    "Favorite Opp. Blocks P/G Home", "Underdog Opp. Blocks P/G Away", "Favorite Steals P/G",
    "Underdog Steals P/G", "Favorite Steals P/G L3", "Underdog Steals P/G L3", "Favorite Steals P/G L1",
    "Underdog Steals P/G L1", "Favorite Steals P/G Home", "Underdog Steals P/G Away",
    "Favorite Opp. Steals P/G", "Underdog Opp. Steals P/G", "Favorite Opp. Steals P/G L3",
    "Underdog Opp. Steals P/G L3", "Favorite Opp. Steals P/G L1", "Underdog Opp. Steals P/G L1",
    "Favorite Opp. Steals P/G Home", "Underdog Opp. Steals P/G Away", "Favorite Steals Per. Defensive Play",
    "Underdog Steals Per. Defensive Play", "Favorite Steals Per. Defensive Play L3",
    "Underdog Steals Per. Defensive Play L3", "Favorite Steals Per. Defensive Play L1",
    "Underdog Steals Per. Defensive Play L1", "Favorite Steals Per. Defensive Play Home",
    "Underdog Steals Per. Defensive Play Away", "Favorite Opp. Steals Per. Defensive Play",
    "Underdog Opp. Steals Per. Defensive Play", "Favorite Opp. Steals Per. Defensive Play L3",
    "Underdog Opp. Steals Per. Defensive Play L3", "Favorite Opp. Steals Per. Defensive Play L1",
    "Underdog Opp. Steals Per. Defensive Play L1", "Favorite Opp. Steals Per. Defensive Play Home",
    "Underdog Opp. Steals Per. Defensive Play Away", "Favorite Assists Per Game", "Underdog Assists Per Game",
    "Favorite Assists Per Game L3", "Underdog Assists Per Game L3", "Favorite Assists Per Game L1",
    "Underdog Assists Per Game L1", "Favorite Assists Per Game Home", "Underdog Assists Per Game Away",
    "Favorite Opp. Assists Per Game", "Underdog Opp. Assists Per Game", "Favorite Opp. Assists Per Game L3",
    "Underdog Opp. Assists Per Game L3", "Favorite Opp. Assists Per Game L1", "Underdog Opp. Assists Per Game L1",
    "Favorite Opp. Assists Per Game Home", "Underdog Opp. Assists Per Game Away", "Favorite Turnovers P/G",
    "Underdog Turnovers P/G", "Favorite Turnovers P/G L3", "Underdog Turnovers P/G L3",
    "Favorite Turnovers P/G L1", "Underdog Turnovers P/G L1", "Favorite Turnovers P/G Home",
    "Underdog Turnovers P/G Away", "Favorite Opp. Turnovers P/G", "Underdog Opp. Turnovers P/G",
    "Favorite Opp. Turnovers P/G L3", "Underdog Opp. Turnovers P/G L3", "Favorite Opp. Turnovers P/G L1",
    "Underdog Opp. Turnovers P/G L1", "Favorite Opp. Turnovers P/G Home", "Underdog Opp. Turnovers P/G Away",
    "Favorite Effective Posession Ratio", "Underdog Effective Posession Ratio",
    "Favorite Effective Posession Ratio L3", "Underdog Effective Posession Ratio L3",
    "Favorite Effective Posession Ratio L1", "Underdog Effective Posession Ratio L1",
    "Favorite Effective Posession Ratio Home", "Underdog Effective Posession Ratio Away",
    "Favorite Opp. Effective Posession Ratio", "Underdog Opp. Effective Posession Ratio",
    "Favorite Opp. Effective Posession Ratio L3", "Underdog Opp. Effective Posession Ratio L3",
    "Favorite Opp. Effective Posession Ratio L1", "Underdog Opp. Effective Posession Ratio L1",
    "Favorite Opp. Effective Posession Ratio Home", "Underdog Opp. Effective Posession Ratio Away",
]

AWAY_PREDICTORS = [
    "Favorite PPG", "Underdog PPG", "Favorite PPG L3", "Underdog PPG L3", "Favorite PPG L1",
    "Underdog PPG L1", "Underdog PPG Home", "Favorite PPG Away", "Favorite PPGA", "Underdog PPGA",
    "Favorite PPGA L3", "Underdog PPGA L3", "Favorite PPGA L1", "Underdog PPGA L1", "Underdog PPGA Home",
    "Favorite PPGA Away", "Favorite Off. Efficiency", "Underdog Off. Efficiency",
    "Favorite Off. Efficiency L3", "Underdog Off. Efficiency L3", "Favorite Off. Efficiency L1",
    "Underdog Off. Efficiency L1", "Underdog Off. Efficiency Home", "Favorite Off. Efficiency Away",
    "Favorite Def. Efficiency", "Underdog Def. Efficiency", "Favorite Def. Efficiency L3",
    "Underdog Def. Efficiency L3", "Favorite Def. Efficiency L1", "Underdog Def. Efficiency L1",
    "Underdog Def. Efficiency Home", "Favorite Def. Efficiency Away", "Favorite Winning % in Close Games",
    "Underdog Winning % in Close Games", "Favorite Opp. Winning % in Close Games",
    "Underdog Opp. Winning % in Close Games", "Favorite 3 Pointers P/G", "Underdog 3 Pointers P/G",
    "Favorite 3 Pointers P/G L3", "Underdog 3 Pointers P/G L3", "Favorite 3 Pointers P/G L1",
    "Underdog 3 Pointers P/G L1", "Underdog 3 Pointers P/G Home", "Favorite 3 Pointers P/G Away",
    "Favorite Opp. 3 Pointers P/G", "Underdog Opp. 3 Pointers P/G", "Favorite Opp. 3 Pointers P/G L3",
    "Underdog Opp. 3 Pointers P/G L3", "Favorite Opp. 3 Pointers P/G L1", "Underdog Opp. 3 Pointers P/G L1",
    "Underdog Opp. 3 Pointers P/G Home", "Favorite Opp. 3 Pointers P/G Away", "Favorite Off. Rebounds P/G",
    "Underdog Off. Rebounds P/G", "Favorite Off. Rebounds P/G L3", "Underdog Off. Rebounds P/G L3",
    "Favorite Off. Rebounds P/G L1", "Underdog Off. Rebounds P/G L1", "Underdog Off. Rebounds P/G Home",
    "Favorite Off. Rebounds P/G Away", "Favorite Def. Rebounds P/G", "Underdog Def. Rebounds P/G",
    "Favorite Def. Rebounds P/G L3", "Underdog Def. Rebounds P/G L3", "Favorite Def. Rebounds P/G L1",
    "Underdog Def. Rebounds P/G L1", "Underdog Def. Rebounds P/G Home", "Favorite Def. Rebounds P/G Away",
    "Favorite Total Rebound %", "Underdog Total Rebound %", "Favorite Total Rebound % L3",
    "Underdog Total Rebound % L3", "Favorite Total Rebound % L1", "Underdog Total Rebound % L1",
    "Underdog Total Rebound % Home", "Favorite Total Rebound % Away", "Favorite Blocks P/G",
    "Underdog Blocks P/G", "Favorite Blocks P/G L3", "Underdog Blocks P/G L3", "Favorite Blocks P/G L1",
    "Underdog Blocks P/G L1", "Underdog Blocks P/G Home", "Favorite Blocks P/G Away",
    "Favorite Opp. Blocks P/G", "Underdog Opp. Blocks P/G", "Favorite Opp. Blocks P/G L3",
    "Underdog Opp. Blocks P/G L3", "Favorite Opp. Blocks P/G L1", "Underdog Opp. Blocks P/G L1",
    "Underdog Opp. Blocks P/G Home", "Favorite Opp. Blocks P/G Away", "Favorite Steals P/G",
    "Underdog Steals P/G", "Favorite Steals P/G L3", "Underdog Steals P/G L3", "Favorite Steals P/G L1",
    "Underdog Steals P/G L1", "Underdog Steals P/G Home", "Favorite Steals P/G Away",
    "Favorite Opp. Steals P/G", "Underdog Opp. Steals P/G", "Favorite Opp. Steals P/G L3",
    "Underdog Opp. Steals P/G L3", "Favorite Opp. Steals P/G L1", "Underdog Opp. Steals P/G L1",
    "Underdog Opp. Steals P/G Home", "Favorite Opp. Steals P/G Away", "Favorite Steals Per. Defensive Play",
    "Underdog Steals Per. Defensive Play", "Favorite Steals Per. Defensive Play L3",
    "Underdog Steals Per. Defensive Play L3", "Favorite Steals Per. Defensive Play L1",
    "Underdog Steals Per. Defensive Play L1", "Underdog Steals Per. Defensive Play Home",
    "Favorite Steals Per. Defensive Play Away", "Favorite Opp. Steals Per. Defensive Play",
    "Underdog Opp. Steals Per. Defensive Play", "Favorite Opp. Steals Per. Defensive Play L3",
    "Underdog Opp. Steals Per. Defensive Play L3", "Favorite Opp. Steals Per. Defensive Play L1",
    "Underdog Opp. Steals Per. Defensive Play L1", "Underdog Opp. Steals Per. Defensive Play Home",
    "Favorite Opp. Steals Per. Defensive Play Away", "Favorite Assists Per Game", "Underdog Assists Per Game",
    "Favorite Assists Per Game L3", "Underdog Assists Per Game L3", "Favorite Assists Per Game L1",
    "Underdog Assists Per Game L1", "Underdog Assists Per Game Home", "Favorite Assists Per Game Away",
    "Favorite Opp. Assists Per Game", "Underdog Opp. Assists Per Game", "Favorite Opp. Assists Per Game L3",
    "Underdog Opp. Assists Per Game L3", "Favorite Opp. Assists Per Game L1", "Underdog Opp. Assists Per Game L1",
    "Underdog Opp. Assists Per Game Home", "Favorite Opp. Assists Per Game Away", "Favorite Turnovers P/G",
    "Underdog Turnovers P/G", "Favorite Turnovers P/G L3", "Underdog Turnovers P/G L3",
    "Favorite Turnovers P/G L1", "Underdog Turnovers P/G L1", "Underdog Turnovers P/G Home",
    "Favorite Turnovers P/G Away", "Favorite Opp. Turnovers P/G", "Underdog Opp. Turnovers P/G",
    "Favorite Opp. Turnovers P/G L3", "Underdog Opp. Turnovers P/G L3", "Favorite Opp. Turnovers P/G L1",
    "Underdog Opp. Turnovers P/G L1", "Underdog Opp. Turnovers P/G Home", "Favorite Opp. Turnovers P/G Away",
    "Favorite Effective Posession Ratio", "Underdog Effective Posession Ratio",
    "Favorite Effective Posession Ratio L3", "Underdog Effective Posession Ratio L3",
    "Favorite Effective Posession Ratio L1", "Underdog Effective Posession Ratio L1",
    "Underdog Effective Posession Ratio Home", "Favorite Effective Posession Ratio Away",
    "Favorite Opp. Effective Posession Ratio", "Underdog Opp. Effective Posession Ratio",
    "Favorite Opp. Effective Posession Ratio L3", "Underdog Opp. Effective Posession Ratio L3",
    "Favorite Opp. Effective Posession Ratio L1", "Underdog Opp. Effective Posession Ratio L1",
    "Underdog Opp. Effective Posession Ratio Home", "Favorite Opp. Effective Posession Ratio Away",
]


class DailySpreadPredictor:
    """
    Daily spread prediction with rolling feature selection and training.
    """
    
    def __init__(self, data_path):
        self.data_path = data_path
        self.df = None
        self.daily_results = []
        
    def load_data(self):
        """Load and prepare the data."""
        print("📊 Loading data from:", self.data_path)
        self.df = pd.read_csv(self.data_path)
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        print(f"✅ Loaded {len(self.df)} total games")
        return self.df
    
    def select_top_features(self, X, y, feature_names, n_features=15):
        """Select top N features using L1 regularization."""
        # Use imputer to handle NaN values during feature selection
        imputer = SimpleImputer(strategy='median')
        X_imputed = imputer.fit_transform(X)
        
        lr = LogisticRegression(max_iter=1000, random_state=42, penalty='l1', solver='saga', C=0.1)
        lr.fit(X_imputed, y)
        coef_abs = np.abs(lr.coef_[0])
        top_indices = np.argsort(coef_abs)[-n_features:][::-1]
        top_features = [feature_names[i] for i in top_indices]
        return top_features
    
    def train_and_predict_day(self, prediction_date):
        """
        Train on data before prediction_date, predict games on that date.
        
        Args:
            prediction_date: Date to predict (as datetime or string)
            
        Returns:
            Dictionary with results for that day
        """
        if isinstance(prediction_date, str):
            prediction_date = pd.to_datetime(prediction_date)
        
        # Split data: training (before prediction date) and prediction (on that date)
        train_df = self.df[self.df['Date'] < prediction_date].copy()
        predict_df = self.df[self.df['Date'] == prediction_date].copy()
        
        if len(predict_df) == 0:
            return None
        
        print(f"\n{'='*80}")
        print(f"📅 DATE: {prediction_date.strftime('%Y-%m-%d')}")
        print(f"{'='*80}")
        print(f"Training on {len(train_df)} games before this date")
        print(f"Predicting {len(predict_df)} games on this date")
        
        # Only use training data with known outcomes
        train_df = train_df[train_df['Favorite Cover?'].notna()]
        
        if len(train_df) < 100:
            print(f"⚠️  Not enough training data ({len(train_df)} games), skipping...")
            return None
        
        day_results = {
            'date': prediction_date.strftime('%Y-%m-%d'),
            'predictions': []
        }
        
        # Process Home Favorite games
        home_fav_train = train_df[train_df['Fav. At Home?'] == 1].copy()
        home_fav_predict = predict_df[predict_df['Fav. At Home?'] == 1].copy()
        
        if len(home_fav_predict) > 0 and len(home_fav_train) >= 50:
            print(f"\n🏠 HOME FAVORITE GAMES: {len(home_fav_predict)}")
            print(f"   Training samples: {len(home_fav_train)}")
            
            # Get available predictors (don't clean NaN yet - let imputer handle it)
            available_predictors = [col for col in HOME_PREDICTORS if col in home_fav_train.columns]
            home_fav_train_clean = home_fav_train.dropna(subset=['Favorite Cover?'])
            
            if len(home_fav_train_clean) >= 50:
                # Select top features
                X_train = home_fav_train_clean[available_predictors].values
                y_train = home_fav_train_clean['Favorite Cover?'].values
                
                top_features = self.select_top_features(X_train, y_train, available_predictors, n_features=15)
                print(f"   Top features selected: {len(top_features)}")
                
                # Create pipeline with imputer, scaler, and model
                pipeline = Pipeline([
                    ('imputer', SimpleImputer(strategy='median')),
                    ('scaler', StandardScaler()),
                    ('model', LogisticRegression(max_iter=1000, random_state=42, C=1.0))
                ])
                
                # Train model
                X_train_top = home_fav_train_clean[top_features].values
                pipeline.fit(X_train_top, y_train)
                
                # Make predictions
                for idx, game in home_fav_predict.iterrows():
                    try:
                        X_pred = game[top_features].values.reshape(1, -1)
                        pred = pipeline.predict(X_pred)[0]
                        proba = pipeline.predict_proba(X_pred)[0][1]
                        
                        actual_cover = game['Favorite Cover?']
                        
                        day_results['predictions'].append({
                            'favorite': game['Favorite'],
                            'underdog': game['Underdog'],
                            'spread': game['Spread'],
                            'fav_at_home': 1,
                            'model': 'Home Favorite',
                            'predicted_cover': int(pred),
                            'cover_probability': proba,
                            'actual_cover': actual_cover if pd.notna(actual_cover) else None,
                            'correct': (pred == actual_cover) if pd.notna(actual_cover) else None
                        })
                    except Exception as e:
                        print(f"   ⚠️  Error predicting game {game['Favorite']} vs {game['Underdog']}: {e}")
        
        # Process Away Favorite games
        away_fav_train = train_df[train_df['Fav. At Home?'] == 0].copy()
        away_fav_predict = predict_df[predict_df['Fav. At Home?'] == 0].copy()
        
        if len(away_fav_predict) > 0 and len(away_fav_train) >= 50:
            print(f"\n✈️  AWAY FAVORITE GAMES: {len(away_fav_predict)}")
            print(f"   Training samples: {len(away_fav_train)}")
            
            # Get available predictors (don't clean NaN yet - let imputer handle it)
            available_predictors = [col for col in AWAY_PREDICTORS if col in away_fav_train.columns]
            away_fav_train_clean = away_fav_train.dropna(subset=['Favorite Cover?'])
            
            if len(away_fav_train_clean) >= 50:
                # Select top features
                X_train = away_fav_train_clean[available_predictors].values
                y_train = away_fav_train_clean['Favorite Cover?'].values
                
                top_features = self.select_top_features(X_train, y_train, available_predictors, n_features=15)
                print(f"   Top features selected: {len(top_features)}")
                
                # Create pipeline with imputer, scaler, and model
                pipeline = Pipeline([
                    ('imputer', SimpleImputer(strategy='median')),
                    ('scaler', StandardScaler()),
                    ('model', LogisticRegression(max_iter=1000, random_state=42, C=1.0))
                ])
                
                # Train model
                X_train_top = away_fav_train_clean[top_features].values
                pipeline.fit(X_train_top, y_train)
                
                # Make predictions
                for idx, game in away_fav_predict.iterrows():
                    try:
                        X_pred = game[top_features].values.reshape(1, -1)
                        pred = pipeline.predict(X_pred)[0]
                        proba = pipeline.predict_proba(X_pred)[0][1]
                        
                        actual_cover = game['Favorite Cover?']
                        
                        day_results['predictions'].append({
                            'favorite': game['Favorite'],
                            'underdog': game['Underdog'],
                            'spread': game['Spread'],
                            'fav_at_home': 0,
                            'model': 'Away Favorite',
                            'predicted_cover': int(pred),
                            'cover_probability': proba,
                            'actual_cover': actual_cover if pd.notna(actual_cover) else None,
                            'correct': (pred == actual_cover) if pd.notna(actual_cover) else None
                        })
                    except Exception as e:
                        print(f"   ⚠️  Error predicting game {game['Favorite']} vs {game['Underdog']}: {e}")
        
        # Print predictions for this day
        if len(day_results['predictions']) > 0:
            print(f"\n📋 PREDICTIONS FOR {prediction_date.strftime('%Y-%m-%d')}:")
            print("-" * 80)
            
            for i, pred in enumerate(day_results['predictions'], 1):
                status = ""
                if pred['actual_cover'] is not None:
                    if pred['correct']:
                        status = "✅ CORRECT"
                    else:
                        status = "❌ WRONG"
                else:
                    status = "⏳ PENDING"
                
                print(f"{i}. {pred['favorite']} vs {pred['underdog']} (Spread: {pred['spread']})")
                print(f"   Prediction: {'COVER' if pred['predicted_cover'] == 1 else 'NO COVER'} "
                      f"({pred['cover_probability']:.1%} confidence) - {status}")
                
                if pred['actual_cover'] is not None:
                    print(f"   Actual: {'COVER' if pred['actual_cover'] == 1 else 'NO COVER'}")
        
        return day_results
    
    def run_daily_predictions(self, start_date='2025-10-21', end_date='2025-11-05'):
        """
        Run predictions for each day in the date range.
        
        Args:
            start_date: First date to predict (YYYY-MM-DD)
            end_date: Last date to predict (YYYY-MM-DD)
        """
        self.load_data()
        
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        print(f"\n{'='*80}")
        print(f"🚀 RUNNING DAILY PREDICTIONS")
        print(f"{'='*80}")
        print(f"Date range: {start_date} to {end_date}")
        
        current_date = start
        while current_date <= end:
            result = self.train_and_predict_day(current_date)
            if result:
                self.daily_results.append(result)
            current_date += timedelta(days=1)
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print overall summary of predictions."""
        print(f"\n\n{'='*80}")
        print("📊 OVERALL SUMMARY")
        print(f"{'='*80}")
        
        total_predictions = sum(len(day['predictions']) for day in self.daily_results)
        predictions_with_results = []
        
        for day in self.daily_results:
            for pred in day['predictions']:
                if pred['actual_cover'] is not None:
                    predictions_with_results.append(pred)
        
        if len(predictions_with_results) > 0:
            correct = sum(1 for p in predictions_with_results if p['correct'])
            accuracy = correct / len(predictions_with_results)
            
            print(f"\nTotal Predictions Made: {total_predictions}")
            print(f"Predictions with Results: {len(predictions_with_results)}")
            print(f"Correct Predictions: {correct}")
            print(f"Overall Accuracy: {accuracy:.2%}")
            
            # Breakdown by model
            home_preds = [p for p in predictions_with_results if p['model'] == 'Home Favorite']
            away_preds = [p for p in predictions_with_results if p['model'] == 'Away Favorite']
            
            if home_preds:
                home_correct = sum(1 for p in home_preds if p['correct'])
                print(f"\n🏠 Home Favorite Model:")
                print(f"   Predictions: {len(home_preds)}")
                print(f"   Accuracy: {home_correct/len(home_preds):.2%}")
            
            if away_preds:
                away_correct = sum(1 for p in away_preds if p['correct'])
                print(f"\n✈️  Away Favorite Model:")
                print(f"   Predictions: {len(away_preds)}")
                print(f"   Accuracy: {away_correct/len(away_preds):.2%}")
            
            # Confidence breakdown
            high_conf = [p for p in predictions_with_results if p['cover_probability'] >= 0.6 or p['cover_probability'] <= 0.4]
            if high_conf:
                high_conf_correct = sum(1 for p in high_conf if p['correct'])
                print(f"\n💪 High Confidence Bets (>60% or <40%):")
                print(f"   Predictions: {len(high_conf)}")
                print(f"   Accuracy: {high_conf_correct/len(high_conf):.2%}")
        else:
            print(f"\nTotal Predictions Made: {total_predictions}")
            print(f"⏳ All predictions are pending (games haven't been played yet)")
        
        # Save results
        self.save_results()
    
    def save_results(self, output_path='./data/daily_predictions_results.csv'):
        """Save all predictions to CSV."""
        all_preds = []
        for day in self.daily_results:
            for pred in day['predictions']:
                pred['date'] = day['date']
                all_preds.append(pred)
        
        if all_preds:
            df_results = pd.DataFrame(all_preds)
            df_results.to_csv(output_path, index=False)
            print(f"\n💾 Results saved to: {output_path}")


def main():
    """Main execution."""
    data_path = '/workspaces/NBA-model/data/NBA Training Set 25-26.csv'
    
    # Load data to find date range automatically
    df = pd.read_csv(data_path)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Find all unique dates in dataset
    all_dates = sorted(df['Date'].unique())
    
    # Get min and max dates (excluding very old historical data if needed)
    # Focus on recent season: filter to dates from 2025-10-21 onwards
    recent_dates = [d for d in all_dates if d >= pd.Timestamp('2025-10-21')]
    
    if len(recent_dates) == 0:
        print("No dates found in the specified range")
        return
    
    start_date = pd.Timestamp(recent_dates[0]).strftime('%Y-%m-%d')
    end_date = pd.Timestamp(recent_dates[-1]).strftime('%Y-%m-%d')
    
    print(f"\n📅 Detected date range in dataset: {start_date} to {end_date}")
    print(f"   Total dates: {len(recent_dates)}")
    
    predictor = DailySpreadPredictor(data_path)
    predictor.run_daily_predictions(start_date=start_date, end_date=end_date)


if __name__ == "__main__":
    main()
