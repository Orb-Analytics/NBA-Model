"""
NBA Spread Prediction - Logistic Regression Model
Author: Orb Analytics (Liam Chaitin)
Purpose: Train logistic regression models to predict game outcomes against the spread
         Uses separate feature sets for home favorite vs away favorite scenarios
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
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


class SpreadPredictionModel:
    """
    Logistic Regression model for predicting NBA games against the spread.
    Trains separate models for home favorite and away favorite scenarios.
    """
    
    def __init__(self, data_path):
        """
        Initialize the model with the path to the training data.
        
        Args:
            data_path: Path to the NBA Training Set CSV
        """
        self.data_path = data_path
        self.df = None
        self.home_fav_model = None
        self.away_fav_model = None
        self.home_fav_scaler = StandardScaler()
        self.away_fav_scaler = StandardScaler()
        self.home_fav_top_features = None
        self.away_fav_top_features = None
        
    def load_data(self):
        """Load and prepare the data."""
        print("📊 Loading data from:", self.data_path)
        self.df = pd.read_csv(self.data_path)
        
        # Filter out rows with missing target variable
        self.df = self.df[self.df['Favorite Cover?'].notna()].copy()
        
        print(f"✅ Loaded {len(self.df)} games with complete data")
        print(f"   - Favorite covers: {self.df['Favorite Cover?'].sum()}")
        print(f"   - Favorite doesn't cover: {len(self.df) - self.df['Favorite Cover?'].sum()}")
        
        return self.df
    
    def select_top_features(self, X, y, feature_names, n_features=15):
        """
        Select top N features using logistic regression coefficients.
        
        Args:
            X: Feature matrix
            y: Target variable
            feature_names: List of feature names
            n_features: Number of top features to select
            
        Returns:
            List of top feature names
        """
        # Train a logistic regression to get feature importance
        lr = LogisticRegression(max_iter=1000, random_state=42, penalty='l1', solver='saga', C=0.1)
        lr.fit(X, y)
        
        # Get absolute coefficients
        coef_abs = np.abs(lr.coef_[0])
        
        # Get top features
        top_indices = np.argsort(coef_abs)[-n_features:][::-1]
        top_features = [feature_names[i] for i in top_indices]
        top_coefs = coef_abs[top_indices]
        
        print(f"\n🔝 Top {n_features} Features:")
        for i, (feat, coef) in enumerate(zip(top_features, top_coefs), 1):
            print(f"   {i:2d}. {feat:50s} | Coefficient: {coef:.4f}")
        
        return top_features
    
    def train_home_favorite_model(self):
        """Train model for games where the favorite is at home."""
        print("\n" + "="*80)
        print("🏠 TRAINING HOME FAVORITE MODEL")
        print("="*80)
        
        # Filter for home favorites
        home_fav_df = self.df[self.df['Fav. At Home?'] == 1].copy()
        print(f"Games where favorite is at home: {len(home_fav_df)}")
        
        # Remove rows with any missing values in predictor columns
        available_predictors = [col for col in HOME_PREDICTORS if col in home_fav_df.columns]
        home_fav_df = home_fav_df.dropna(subset=available_predictors)
        print(f"Games with complete data: {len(home_fav_df)}")
        
        # Prepare features and target
        X = home_fav_df[available_predictors].values
        y = home_fav_df['Favorite Cover?'].values
        
        # Select top 15 features
        print("\n🔍 Performing feature selection for HOME FAVORITE scenario...")
        self.home_fav_top_features = self.select_top_features(X, y, available_predictors, n_features=15)
        
        # Train final model with top features
        X_top = home_fav_df[self.home_fav_top_features].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_top, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.home_fav_scaler.fit_transform(X_train)
        X_test_scaled = self.home_fav_scaler.transform(X_test)
        
        # Train model
        print("\n🤖 Training final logistic regression model...")
        self.home_fav_model = LogisticRegression(max_iter=1000, random_state=42, C=1.0)
        self.home_fav_model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_preds = self.home_fav_model.predict(X_train_scaled)
        test_preds = self.home_fav_model.predict(X_test_scaled)
        
        train_acc = accuracy_score(y_train, train_preds)
        test_acc = accuracy_score(y_test, test_preds)
        
        print(f"\n📈 Model Performance:")
        print(f"   Training Accuracy: {train_acc:.4f}")
        print(f"   Test Accuracy: {test_acc:.4f}")
        
        # Cross-validation
        cv_scores = cross_val_score(self.home_fav_model, X_train_scaled, y_train, cv=5)
        print(f"   Cross-Val Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # Classification report
        print(f"\n📊 Classification Report (Test Set):")
        print(classification_report(y_test, test_preds, target_names=['No Cover', 'Cover']))
        
        # Confusion matrix
        cm = confusion_matrix(y_test, test_preds)
        print(f"\n🔢 Confusion Matrix:")
        print(f"   Predicted No Cover | Predicted Cover")
        print(f"   {cm[0][0]:18d} | {cm[0][1]:15d}  (Actual No Cover)")
        print(f"   {cm[1][0]:18d} | {cm[1][1]:15d}  (Actual Cover)")
        
        # ROC AUC
        test_proba = self.home_fav_model.predict_proba(X_test_scaled)[:, 1]
        roc_auc = roc_auc_score(y_test, test_proba)
        print(f"\n🎯 ROC AUC Score: {roc_auc:.4f}")
        
        return self.home_fav_model
    
    def train_away_favorite_model(self):
        """Train model for games where the favorite is away."""
        print("\n" + "="*80)
        print("✈️  TRAINING AWAY FAVORITE MODEL")
        print("="*80)
        
        # Filter for away favorites
        away_fav_df = self.df[self.df['Fav. At Home?'] == 0].copy()
        print(f"Games where favorite is away: {len(away_fav_df)}")
        
        # Remove rows with any missing values in predictor columns
        available_predictors = [col for col in AWAY_PREDICTORS if col in away_fav_df.columns]
        away_fav_df = away_fav_df.dropna(subset=available_predictors)
        print(f"Games with complete data: {len(away_fav_df)}")
        
        # Prepare features and target
        X = away_fav_df[available_predictors].values
        y = away_fav_df['Favorite Cover?'].values
        
        # Select top 15 features
        print("\n🔍 Performing feature selection for AWAY FAVORITE scenario...")
        self.away_fav_top_features = self.select_top_features(X, y, available_predictors, n_features=15)
        
        # Train final model with top features
        X_top = away_fav_df[self.away_fav_top_features].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_top, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.away_fav_scaler.fit_transform(X_train)
        X_test_scaled = self.away_fav_scaler.transform(X_test)
        
        # Train model
        print("\n🤖 Training final logistic regression model...")
        self.away_fav_model = LogisticRegression(max_iter=1000, random_state=42, C=1.0)
        self.away_fav_model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_preds = self.away_fav_model.predict(X_train_scaled)
        test_preds = self.away_fav_model.predict(X_test_scaled)
        
        train_acc = accuracy_score(y_train, train_preds)
        test_acc = accuracy_score(y_test, test_preds)
        
        print(f"\n📈 Model Performance:")
        print(f"   Training Accuracy: {train_acc:.4f}")
        print(f"   Test Accuracy: {test_acc:.4f}")
        
        # Cross-validation
        cv_scores = cross_val_score(self.away_fav_model, X_train_scaled, y_train, cv=5)
        print(f"   Cross-Val Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # Classification report
        print(f"\n📊 Classification Report (Test Set):")
        print(classification_report(y_test, test_preds, target_names=['No Cover', 'Cover']))
        
        # Confusion matrix
        cm = confusion_matrix(y_test, test_preds)
        print(f"\n🔢 Confusion Matrix:")
        print(f"   Predicted No Cover | Predicted Cover")
        print(f"   {cm[0][0]:18d} | {cm[0][1]:15d}  (Actual No Cover)")
        print(f"   {cm[1][0]:18d} | {cm[1][1]:15d}  (Actual Cover)")
        
        # ROC AUC
        test_proba = self.away_fav_model.predict_proba(X_test_scaled)[:, 1]
        roc_auc = roc_auc_score(y_test, test_proba)
        print(f"\n🎯 ROC AUC Score: {roc_auc:.4f}")
        
        return self.away_fav_model
    
    def predict(self, game_data):
        """
        Make predictions for new games.
        
        Args:
            game_data: DataFrame with game features
            
        Returns:
            DataFrame with predictions and probabilities
        """
        predictions = []
        
        for idx, row in game_data.iterrows():
            fav_at_home = row['Fav. At Home?']
            
            if fav_at_home == 1:
                # Use home favorite model
                features = row[self.home_fav_top_features].values.reshape(1, -1)
                features_scaled = self.home_fav_scaler.transform(features)
                pred = self.home_fav_model.predict(features_scaled)[0]
                proba = self.home_fav_model.predict_proba(features_scaled)[0][1]
                model_used = 'Home Favorite'
            else:
                # Use away favorite model
                features = row[self.away_fav_top_features].values.reshape(1, -1)
                features_scaled = self.away_fav_scaler.transform(features)
                pred = self.away_fav_model.predict(features_scaled)[0]
                proba = self.away_fav_model.predict_proba(features_scaled)[0][1]
                model_used = 'Away Favorite'
            
            predictions.append({
                'Favorite': row.get('Favorite', 'Unknown'),
                'Underdog': row.get('Underdog', 'Unknown'),
                'Spread': row.get('Spread', 'Unknown'),
                'Fav_At_Home': fav_at_home,
                'Model_Used': model_used,
                'Predicted_Cover': 'Yes' if pred == 1 else 'No',
                'Cover_Probability': proba
            })
        
        return pd.DataFrame(predictions)
    
    def train_all(self):
        """Train both models."""
        self.load_data()
        self.train_home_favorite_model()
        self.train_away_favorite_model()
        
        print("\n" + "="*80)
        print("✅ MODEL TRAINING COMPLETE")
        print("="*80)
        print(f"🏠 Home Favorite Model: Using {len(self.home_fav_top_features)} features")
        print(f"✈️  Away Favorite Model: Using {len(self.away_fav_top_features)} features")
        
    def save_feature_lists(self, output_path='./data/selected_features.txt'):
        """Save the selected features to a file."""
        with open(output_path, 'w') as f:
            f.write("HOME FAVORITE MODEL - TOP 15 FEATURES\n")
            f.write("="*80 + "\n")
            for i, feat in enumerate(self.home_fav_top_features, 1):
                f.write(f"{i:2d}. {feat}\n")
            
            f.write("\n\nAWAY FAVORITE MODEL - TOP 15 FEATURES\n")
            f.write("="*80 + "\n")
            for i, feat in enumerate(self.away_fav_top_features, 1):
                f.write(f"{i:2d}. {feat}\n")
        
        print(f"\n💾 Feature lists saved to: {output_path}")


def main():
    """Main execution function."""
    # Path to the training data
    data_path = '/workspaces/NBA-model/data/NBA Training Set 25-26.csv'
    
    # Initialize and train the model
    model = SpreadPredictionModel(data_path)
    model.train_all()
    
    # Save feature lists
    model.save_feature_lists()
    
    print("\n🎉 Training complete! Models are ready for predictions.")


if __name__ == "__main__":
    main()
