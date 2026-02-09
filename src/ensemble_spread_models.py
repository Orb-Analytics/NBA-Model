"""
NBA Spread Prediction - Ensemble Models (3 Models)
Author: Orb Analytics (Liam Chaitin)
Purpose: Train 3 models (Logistic, Linear, Random Forest) for spread prediction
         Uses same framework: separate feature sets for home vs away favorites
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression, LinearRegression, Lasso
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, mean_absolute_error, mean_squared_error
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Feature sets for home vs away favorites
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

class EnsembleSpreadPredictor:
    """
    Ensemble predictor using multiple model types.
    Each model predicts whether the favorite will cover the spread.
    """
    
    def __init__(self, data_path):
        self.data_path = data_path
        self.df = None
        
        # Models for Home Favorite scenario (3 models: Logistic, Linear, RF)
        self.home_models = {
            'logistic': LogisticRegression(penalty='l1', C=0.1, solver='liblinear', max_iter=1000, random_state=42),
            'linear': LinearRegression(),
            'random_forest': RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        }
        
        # Models for Away Favorite scenario (3 models: Logistic, Linear, RF)
        self.away_models = {
            'logistic': LogisticRegression(penalty='l1', C=0.1, solver='liblinear', max_iter=1000, random_state=42),
            'linear': LinearRegression(),
            'random_forest': RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        }
        
        self.home_scalers = {}
        self.away_scalers = {}
        self.home_features = None
        self.away_features = None
    
    def load_data(self, verbose=True):
        """Load and prepare data."""
        if verbose:
            print(f"📂 Loading data from {self.data_path}")
        
        self.df = pd.read_csv(self.data_path)
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        
        if verbose:
            print(f"✅ Loaded {len(self.df)} games")
    
    def select_features(self, X, y, predictors, top_n=15):
        """
        Select top N features using L1 regularization (Lasso).
        Same method as the logistic model.
        """
        # Impute missing values
        imputer = SimpleImputer(strategy='mean')
        X_imputed = imputer.fit_transform(X)
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_imputed)
        
        # Use Lasso to select features
        lasso = Lasso(alpha=0.01, random_state=42)
        lasso.fit(X_scaled, y)
        
        # Get feature importance
        feature_importance = np.abs(lasso.coef_)
        top_indices = np.argsort(feature_importance)[-top_n:]
        selected_features = [predictors[i] for i in top_indices]
        
        return selected_features
    
    def train_models(self, train_date, verbose=True):
        """
        Train all models on data before train_date.
        Selects features dynamically like the original logistic model.
        """
        # Filter training data (only games before train_date)
        train_df = self.df[self.df['Date'] < pd.to_datetime(train_date)].copy()
        
        # Only use games with complete data
        train_df = train_df.dropna(subset=['Favorite Cover?'])
        
        if len(train_df) == 0:
            if verbose:
                print("⚠️ No training data available")
            return False
        
        # Separate by home vs away favorite
        home_fav_train = train_df[train_df['Fav. At Home?'] == 1]
        away_fav_train = train_df[train_df['Fav. At Home?'] == 0]
        
        if verbose:
            print(f"Training on {len(train_df)} games before {train_date}")
        
        # Train HOME FAVORITE models
        if len(home_fav_train) > 50:
            X_home = home_fav_train[HOME_PREDICTORS]
            y_home = home_fav_train['Favorite Cover?']
            
            # Select top features
            self.home_features = self.select_features(X_home, y_home, HOME_PREDICTORS, top_n=15)
            X_home_selected = home_fav_train[self.home_features]
            
            # Train each model
            for model_name, model in self.home_models.items():
                # Create pipeline
                if model_name == 'linear':
                    # Linear regression needs continuous target for training
                    pipeline = Pipeline([
                        ('imputer', SimpleImputer(strategy='mean')),
                        ('scaler', StandardScaler()),
                        ('model', model)
                    ])
                else:
                    pipeline = Pipeline([
                        ('imputer', SimpleImputer(strategy='mean')),
                        ('scaler', StandardScaler()),
                        ('model', model)
                    ])
                
                pipeline.fit(X_home_selected, y_home)
                self.home_scalers[model_name] = pipeline
            
            if verbose:
                print(f"🏠 HOME FAVORITE: Trained {len(self.home_models)} models on {len(home_fav_train)} games")
                print(f"   Selected features: {len(self.home_features)}")
        
        # Train AWAY FAVORITE models
        if len(away_fav_train) > 50:
            X_away = away_fav_train[AWAY_PREDICTORS]
            y_away = away_fav_train['Favorite Cover?']
            
            # Select top features
            self.away_features = self.select_features(X_away, y_away, AWAY_PREDICTORS, top_n=15)
            X_away_selected = away_fav_train[self.away_features]
            
            # Train each model
            for model_name, model in self.away_models.items():
                if model_name == 'linear':
                    pipeline = Pipeline([
                        ('imputer', SimpleImputer(strategy='mean')),
                        ('scaler', StandardScaler()),
                        ('model', model)
                    ])
                else:
                    pipeline = Pipeline([
                        ('imputer', SimpleImputer(strategy='mean')),
                        ('scaler', StandardScaler()),
                        ('model', model)
                    ])
                
                pipeline.fit(X_away_selected, y_away)
                self.away_scalers[model_name] = pipeline
            
            if verbose:
                print(f"✈️  AWAY FAVORITE: Trained {len(self.away_models)} models on {len(away_fav_train)} games")
                print(f"   Selected features: {len(self.away_features)}")
        
        return True
    
    def predict_game(self, game_row):
        """
        Make predictions using all models for a single game.
        Returns dict with predictions from each model.
        """
        fav_at_home = int(game_row['Fav. At Home?'])
        
        # Choose model set and features
        if fav_at_home == 1:
            models = self.home_scalers
            features = self.home_features
            model_type = "Home Favorite"
        else:
            models = self.away_scalers
            features = self.away_features
            model_type = "Away Favorite"
        
        if not features or not models:
            return None
        
        # Prepare game data
        X_game = game_row[features].values.reshape(1, -1)
        
        predictions = {
            'favorite': game_row['Favorite'],
            'underdog': game_row['Underdog'],
            'spread': game_row['Spread'],
            'fav_at_home': fav_at_home,
            'model_type': model_type,
            'date': game_row['Date']
        }
        
        # Get predictions from each model
        for model_name, pipeline in models.items():
            if model_name == 'linear':
                # Linear regression outputs continuous value
                raw_pred = pipeline.predict(X_game)[0]
                # Convert to probability (clip between 0 and 1)
                probability = np.clip(raw_pred, 0, 1)
                predicted_cover = 1 if probability > 0.5 else 0
            elif model_name == 'logistic':
                # Logistic outputs probability
                probability = pipeline.predict_proba(X_game)[0][1]
                predicted_cover = 1 if probability > 0.5 else 0
            else:
                # Tree models output class
                predicted_cover = pipeline.predict(X_game)[0]
                # Get probability if available
                if hasattr(pipeline.named_steps['model'], 'predict_proba'):
                    probability = pipeline.predict_proba(X_game)[0][1]
                else:
                    probability = predicted_cover
            
            predictions[f'{model_name}_probability'] = probability
            predictions[f'{model_name}_prediction'] = predicted_cover
        
        return predictions
    
    def predict_date(self, date, verbose=True):
        """
        Predict all games on a specific date using all models.
        """
        date_str = pd.to_datetime(date).strftime('%Y-%m-%d')
        games = self.df[self.df['Date'] == date_str]
        
        if len(games) == 0:
            if verbose:
                print(f"No games found on {date_str}")
            return []
        
        predictions = []
        for idx, game in games.iterrows():
            pred = self.predict_game(game)
            if pred:
                predictions.append(pred)
        
        return predictions
    
    def evaluate_models(self, start_date='2025-10-22', end_date='2025-11-16', verbose=True):
        """
        Evaluate all models on historical data using rolling predictions.
        """
        results = []
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            
            # Train on data before this date
            self.train_models(date_str, verbose=False)
            
            # Predict for this date
            predictions = self.predict_date(date_str, verbose=False)
            
            if not predictions:
                continue
            
            # Check actual results
            for pred in predictions:
                game_actual = self.df[
                    (self.df['Date'] == date_str) &
                    (self.df['Favorite'] == pred['favorite']) &
                    (self.df['Underdog'] == pred['underdog'])
                ]
                
                if not game_actual.empty and pd.notna(game_actual.iloc[0]['Favorite Cover?']):
                    actual_cover = int(game_actual.iloc[0]['Favorite Cover?'])
                    
                    # Store results for each model (3 models only)
                    for model_name in ['logistic', 'linear', 'random_forest']:
                        result = {
                            'date': date_str,
                            'favorite': pred['favorite'],
                            'underdog': pred['underdog'],
                            'spread': pred['spread'],
                            'model_name': model_name,
                            'model_type': pred['model_type'],
                            'probability': pred[f'{model_name}_probability'],
                            'predicted_cover': pred[f'{model_name}_prediction'],
                            'actual_cover': actual_cover,
                            'correct': pred[f'{model_name}_prediction'] == actual_cover
                        }
                        results.append(result)
        
        results_df = pd.DataFrame(results)
        
        if verbose and len(results_df) > 0:
            print("\n" + "="*80)
            print("📊 MODEL COMPARISON")
            print("="*80)
            
            for model_name in ['logistic', 'linear', 'random_forest']:
                model_results = results_df[results_df['model_name'] == model_name]
                if len(model_results) > 0:
                    accuracy = model_results['correct'].mean() * 100
                    total = len(model_results)
                    correct = model_results['correct'].sum()
                    
                    print(f"\n{model_name.upper()}:")
                    print(f"   Accuracy: {accuracy:.2f}% ({correct}/{total})")
                    
                    # By model type
                    home_results = model_results[model_results['model_type'] == 'Home Favorite']
                    away_results = model_results[model_results['model_type'] == 'Away Favorite']
                    
                    if len(home_results) > 0:
                        home_acc = home_results['correct'].mean() * 100
                        print(f"   🏠 Home Favorite: {home_acc:.2f}% ({home_results['correct'].sum()}/{len(home_results)})")
                    
                    if len(away_results) > 0:
                        away_acc = away_results['correct'].mean() * 100
                        print(f"   ✈️  Away Favorite: {away_acc:.2f}% ({away_results['correct'].sum()}/{len(away_results)})")
        
        return results_df


def backtest_individual_model(model_name, start_date='2025-10-22', end_date='2025-11-16'):
    """
    Backtest a single model type.
    
    Args:
        model_name: 'logistic', 'linear', or 'random_forest'
        start_date: Start date for backtesting
        end_date: End date for backtesting
    """
    print(f"\n{'='*80}")
    print(f"🔬 BACKTESTING: {model_name.upper().replace('_', ' ')}")
    print(f"{'='*80}")
    print(f"Period: {start_date} to {end_date}\n")
    
    predictor = EnsembleSpreadPredictor('data/NBA Training Set 25-26.csv')
    predictor.load_data(verbose=False)
    
    results = []
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    for date in dates:
        date_str = date.strftime('%Y-%m-%d')
        
        # Train on data before this date
        predictor.train_models(date_str, verbose=False)
        
        # Predict for this date
        predictions = predictor.predict_date(date_str, verbose=False)
        
        if not predictions:
            continue
        
        # Check actual results
        for pred in predictions:
            game_actual = predictor.df[
                (predictor.df['Date'] == date_str) &
                (predictor.df['Favorite'] == pred['favorite']) &
                (predictor.df['Underdog'] == pred['underdog'])
            ]
            
            if not game_actual.empty and pd.notna(game_actual.iloc[0]['Favorite Cover?']):
                actual_cover = int(game_actual.iloc[0]['Favorite Cover?'])
                
                result = {
                    'date': date_str,
                    'favorite': pred['favorite'],
                    'underdog': pred['underdog'],
                    'spread': pred['spread'],
                    'model_name': model_name,
                    'model_type': pred['model_type'],
                    'probability': pred[f'{model_name}_probability'],
                    'predicted_cover': pred[f'{model_name}_prediction'],
                    'actual_cover': actual_cover,
                    'correct': pred[f'{model_name}_prediction'] == actual_cover
                }
                results.append(result)
    
    results_df = pd.DataFrame(results)
    
    if len(results_df) > 0:
        # Overall stats
        accuracy = results_df['correct'].mean() * 100
        total = len(results_df)
        correct = results_df['correct'].sum()
        
        print(f"📊 OVERALL PERFORMANCE")
        print(f"   Accuracy: {accuracy:.2f}% ({correct}/{total})")
        print(f"   Avg Probability: {results_df['probability'].mean()*100:.2f}%")
        
        # By model type
        home_results = results_df[results_df['model_type'] == 'Home Favorite']
        away_results = results_df[results_df['model_type'] == 'Away Favorite']
        
        print(f"\n📍 BY SCENARIO")
        if len(home_results) > 0:
            home_acc = home_results['correct'].mean() * 100
            print(f"   🏠 Home Favorite: {home_acc:.2f}% ({home_results['correct'].sum()}/{len(home_results)})")
        
        if len(away_results) > 0:
            away_acc = away_results['correct'].mean() * 100
            print(f"   ✈️  Away Favorite: {away_acc:.2f}% ({away_results['correct'].sum()}/{len(away_results)})")
        
        # Weekly breakdown
        results_df['week'] = pd.to_datetime(results_df['date']).dt.isocalendar().week
        print(f"\n📅 WEEKLY BREAKDOWN")
        for week, week_df in results_df.groupby('week'):
            week_acc = week_df['correct'].mean() * 100
            week_start = week_df['date'].min()
            week_end = week_df['date'].max()
            print(f"   Week {week} ({week_start} to {week_end}): {week_acc:.2f}% ({week_df['correct'].sum()}/{len(week_df)})")
        
        # Save individual results
        output_file = f'data/{model_name}_model_results.csv'
        results_df.to_csv(output_file, index=False)
        print(f"\n💾 Results saved to {output_file}")
    else:
        print("⚠️ No results to display")
    
    print(f"{'='*80}\n")
    
    return results_df


def main():
    """Run backtesting for each model separately."""
    import sys
    
    if len(sys.argv) > 1:
        # Backtest specific model
        model_name = sys.argv[1].lower()
        if model_name in ['logistic', 'linear', 'random_forest']:
            backtest_individual_model(model_name)
        else:
            print(f"❌ Invalid model name: {model_name}")
            print("Valid options: logistic, linear, random_forest")
    else:
        # Backtest all models (3 models only)
        all_results = []
        
        for model_name in ['logistic', 'linear', 'random_forest']:
            results_df = backtest_individual_model(model_name)
            all_results.append(results_df)
        
        # Combine all results
        combined_df = pd.concat(all_results, ignore_index=True)
        combined_df.to_csv('data/ensemble_model_results.csv', index=False)
        print(f"💾 Combined results saved to data/ensemble_model_results.csv")


if __name__ == "__main__":
    main()
