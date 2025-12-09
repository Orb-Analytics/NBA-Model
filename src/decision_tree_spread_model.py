"""
NBA Spread Prediction - Decision Tree Model
Author: Orb Analytics (Liam Chaitin)
Purpose: Backtest decision tree model with detailed output
"""

import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import Lasso
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import feature sets from daily_spread_predictions
from daily_spread_predictions import HOME_PREDICTORS, AWAY_PREDICTORS


def american_odds_to_probability(odds):
    """Convert American odds to implied probability."""
    if pd.isna(odds):
        return np.nan
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)
    else:
        return 100 / (odds + 100)


class DecisionTreeSpreadModel:
    """Decision Tree model for NBA spread prediction."""
    
    def __init__(self, data_path):
        self.data_path = data_path
        self.df = None
        self.home_model = DecisionTreeClassifier(max_depth=5, random_state=42)
        self.away_model = DecisionTreeClassifier(max_depth=5, random_state=42)
        self.home_pipeline = None
        self.away_pipeline = None
        self.home_features = None
        self.away_features = None
    
    def load_data(self):
        """Load and prepare data."""
        self.df = pd.read_csv(self.data_path)
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        print(f"✅ Loaded {len(self.df)} games")
    
    def select_features(self, X, y, predictors, top_n=15):
        """Select top N features using L1 regularization."""
        imputer = SimpleImputer(strategy='mean')
        X_imputed = imputer.fit_transform(X)
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_imputed)
        
        lasso = Lasso(alpha=0.01, random_state=42)
        lasso.fit(X_scaled, y)
        
        feature_importance = np.abs(lasso.coef_)
        top_indices = np.argsort(feature_importance)[-top_n:]
        selected_features = [predictors[i] for i in top_indices]
        
        return selected_features
    
    def train_models(self, train_date):
        """Train models on data before train_date."""
        train_df = self.df[self.df['Date'] < pd.to_datetime(train_date)].copy()
        train_df = train_df.dropna(subset=['Favorite Cover?'])
        
        if len(train_df) == 0:
            return False
        
        # Train HOME FAVORITE model
        home_fav_train = train_df[train_df['Fav. At Home?'] == 1]
        if len(home_fav_train) > 50:
            X_home = home_fav_train[HOME_PREDICTORS]
            y_home = home_fav_train['Favorite Cover?']
            
            self.home_features = self.select_features(X_home, y_home, HOME_PREDICTORS, top_n=15)
            X_home_selected = home_fav_train[self.home_features]
            
            self.home_pipeline = Pipeline([
                ('imputer', SimpleImputer(strategy='mean')),
                ('scaler', StandardScaler()),
                ('model', self.home_model)
            ])
            self.home_pipeline.fit(X_home_selected, y_home)
        
        # Train AWAY FAVORITE model
        away_fav_train = train_df[train_df['Fav. At Home?'] == 0]
        if len(away_fav_train) > 50:
            X_away = away_fav_train[AWAY_PREDICTORS]
            y_away = away_fav_train['Favorite Cover?']
            
            self.away_features = self.select_features(X_away, y_away, AWAY_PREDICTORS, top_n=15)
            X_away_selected = away_fav_train[self.away_features]
            
            self.away_pipeline = Pipeline([
                ('imputer', SimpleImputer(strategy='mean')),
                ('scaler', StandardScaler()),
                ('model', self.away_model)
            ])
            self.away_pipeline.fit(X_away_selected, y_away)
        
        return True
    
    def predict_game(self, game_row):
        """Make prediction for a single game."""
        fav_at_home = int(game_row['Fav. At Home?'])
        
        if fav_at_home == 1:
            pipeline = self.home_pipeline
            features = self.home_features
            model_type = "Home Favorite"
        else:
            pipeline = self.away_pipeline
            features = self.away_features
            model_type = "Away Favorite"
        
        if not features or not pipeline:
            return None
        
        X_game = game_row[features].values.reshape(1, -1)
        
        # Get probability that favorite covers
        model_fav_probability = pipeline.predict_proba(X_game)[0][1]
        model_dog_probability = 1 - model_fav_probability
        predicted_cover = 1 if model_fav_probability > 0.5 else 0
        
        # Get odds data
        fav_odds = game_row.get('Fav. Odds', np.nan)
        dog_odds = game_row.get('Dog Odds', np.nan)
        
        # Calculate implied probabilities
        fav_implied_prob = american_odds_to_probability(fav_odds)
        dog_implied_prob = american_odds_to_probability(dog_odds)
        
        # Calculate predictive edges
        fav_predictive_edge = model_fav_probability - fav_implied_prob if pd.notna(fav_implied_prob) else np.nan
        dog_predictive_edge = model_dog_probability - dog_implied_prob if pd.notna(dog_implied_prob) else np.nan
        
        # Determine best edge
        if pd.notna(fav_predictive_edge) and pd.notna(dog_predictive_edge):
            if fav_predictive_edge > dog_predictive_edge:
                best_edge = fav_predictive_edge
                best_side = 'favorite'
            else:
                best_edge = dog_predictive_edge
                best_side = 'underdog'
        else:
            best_edge = np.nan
            best_side = np.nan
        
        return {
            'date': game_row['Date'].strftime('%Y-%m-%d'),
            'favorite': game_row['Favorite'],
            'underdog': game_row['Underdog'],
            'spread': game_row['Spread'],
            'fav_odds': fav_odds,
            'dog_odds': dog_odds,
            'fav_implied_prob': fav_implied_prob,
            'dog_implied_prob': dog_implied_prob,
            'model_fav_probability': model_fav_probability,
            'model_dog_probability': model_dog_probability,
            'fav_predictive_edge': fav_predictive_edge,
            'dog_predictive_edge': dog_predictive_edge,
            'best_edge': best_edge,
            'best_side': best_side,
            'predicted_cover': predicted_cover,
            'actual_cover': game_row.get('Favorite Cover?', np.nan),
            'correct_prediction': np.nan,
            'model_type': model_type
        }
    
    def backtest(self, start_date='2025-10-22', end_date='2025-11-16'):
        """Run backtest and return detailed results."""
        print(f"\n{'='*80}")
        print(f"🔬 BACKTESTING: DECISION TREE")
        print(f"{'='*80}")
        print(f"Period: {start_date} to {end_date}\n")
        
        results = []
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            
            # Train on data before this date
            self.train_models(date_str)
            
            # Get games for this date
            games = self.df[self.df['Date'] == date_str]
            
            for idx, game in games.iterrows():
                pred = self.predict_game(game)
                if pred and pd.notna(pred['actual_cover']):
                    pred['correct_prediction'] = int(pred['predicted_cover'] == pred['actual_cover'])
                    results.append(pred)
        
        results_df = pd.DataFrame(results)
        
        if len(results_df) > 0:
            accuracy = results_df['correct_prediction'].mean() * 100
            correct = results_df['correct_prediction'].sum()
            total = len(results_df)
            
            print(f"📊 OVERALL PERFORMANCE")
            print(f"   Accuracy: {accuracy:.2f}% ({correct}/{total})")
            
            # By model type
            for model_type in ['Home Favorite', 'Away Favorite']:
                subset = results_df[results_df['model_type'] == model_type]
                if len(subset) > 0:
                    acc = subset['correct_prediction'].mean() * 100
                    icon = "🏠" if model_type == "Home Favorite" else "✈️ "
                    print(f"   {icon} {model_type}: {acc:.2f}% ({subset['correct_prediction'].sum()}/{len(subset)})")
            
            # Save results
            output_file = 'data/decision_tree_model_results.csv'
            results_df.to_csv(output_file, index=False)
            print(f"\n💾 Results saved to {output_file}")
            print(f"{'='*80}\n")
        
        return results_df


def main():
    """Run decision tree model backtest."""
    model = DecisionTreeSpreadModel('data/NBA Training Set 25-26.csv')
    model.load_data()
    model.backtest()


if __name__ == "__main__":
    main()
