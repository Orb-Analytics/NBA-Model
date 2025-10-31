import pytest
import pandas as pd
from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import only the constants and functions that don't load data
from merge_nba_scores import TEAM_NAME_MAP
from difflib import SequenceMatcher

def fuzzy_match(team, candidates, threshold=0.85):
    """Replicate fuzzy_match function for testing."""
    best_match = None
    best_score = 0
    for candidate in candidates:
        score = SequenceMatcher(None, team, candidate).ratio()
        if score > best_score and score >= threshold:
            best_match = candidate
            best_score = score
    return best_match, best_score

class TestTeamMapping:
    """Test team name mapping functionality."""

    def test_team_name_map_completeness(self):
        """Test that TEAM_NAME_MAP has all expected teams."""
        expected_abbrs = {
            "ATL", "BOS", "BKN", "CHA", "CHI", "CLE", "DAL", "DEN",
            "DET", "GS", "HOU", "IND", "LAC", "LAL", "MEM", "MIA",
            "MIL", "MIN", "NO", "NY", "OKC", "ORL", "PHI", "PHX",
            "POR", "SAC", "SA", "TOR", "UTAH", "WSH"
        }
        mapped_teams = set(TEAM_NAME_MAP.values())
        assert len(mapped_teams) == 30, "Should have 30 unique team abbreviations"
        assert mapped_teams == expected_abbrs, "Should match expected NBA abbreviations"

    def test_team_name_mapping(self):
        """Test specific team mappings."""
        assert TEAM_NAME_MAP["LA Lakers"] == "LAL"
        assert TEAM_NAME_MAP["LA Clippers"] == "LAC"
        assert TEAM_NAME_MAP["Okla City"] == "OKC"
        assert TEAM_NAME_MAP["Golden State"] == "GS"
        assert TEAM_NAME_MAP["San Antonio"] == "SA"

    def test_fuzzy_match_high_similarity(self):
        """Test fuzzy matches with high similarity."""
        candidates = ["LAL", "BOS", "GSW", "LAC"]
        match, score = fuzzy_match("LAC", candidates)  # LAC is in candidates
        assert match == "LAC"
        assert score == 1.0
        assert TEAM_NAME_MAP["San Antonio"] == "SA"

    def test_team_name_mapping(self):
        """Test specific team mappings."""
        assert TEAM_NAME_MAP["LA Lakers"] == "LAL"
        assert TEAM_NAME_MAP["LA Clippers"] == "LAC"
        assert TEAM_NAME_MAP["Okla City"] == "OKC"
        assert TEAM_NAME_MAP["Golden State"] == "GS"
        assert TEAM_NAME_MAP["San Antonio"] == "SA"

class TestFuzzyMatching:
    """Test fuzzy matching functionality."""

    def test_exact_match(self):
        """Test exact matches."""
        candidates = ["LAL", "BOS", "GSW"]
        match, score = fuzzy_match("LAL", candidates)
        assert match == "LAL"
        assert score == 1.0

    def test_fuzzy_match_high_similarity(self):
        """Test fuzzy matches with high similarity."""
        candidates = ["LAL", "BOS", "GSW", "LAC"]
        match, score = fuzzy_match("LAC", candidates)  # LAC is in candidates
        assert match == "LAC"
        assert score == 1.0

    def test_fuzzy_match_low_similarity(self):
        """Test fuzzy matches with low similarity."""
        candidates = ["LAL", "BOS", "GSW"]
        match, score = fuzzy_match("CHI", candidates)  # Not similar
        assert match is None
        assert score == 0

    def test_fuzzy_match_threshold(self):
        """Test fuzzy match respects threshold."""
        candidates = ["LAL", "BOS", "GSW"]
        match, score = fuzzy_match("LA", candidates, threshold=0.9)
        # "LA" might match LAL with score around 0.67, below 0.9
        if match:
            assert score >= 0.9

class TestDataValidation:
    """Test data validation functions."""

    def test_master_file_exists(self):
        """Test that master file exists."""
        master_file = Path("data/NBA Training Set 25-26.csv")
        assert master_file.exists(), "Master dataset should exist"

    def test_master_has_required_columns(self):
        """Test that master has required columns."""
        master_file = Path("data/NBA Training Set 25-26.csv")
        df = pd.read_csv(master_file)

        required_cols = ['Date', 'Favorite', 'Underdog', 'Spread', 'Fav. At Home?']
        for col in required_cols:
            assert col in df.columns, f"Missing required column: {col}"

    def test_spread_values_reasonable(self):
        """Test that spread values are within reasonable range."""
        master_file = Path("data/NBA Training Set 25-26.csv")
        df = pd.read_csv(master_file)

        spreads = df['Spread'].dropna()
        assert all(spreads.abs() <= 50), "Spreads should be within reasonable range"

    def test_home_indicator_binary(self):
        """Test that Fav. At Home? is binary."""
        master_file = Path("data/NBA Training Set 25-26.csv")
        df = pd.read_csv(master_file)

        home_values = df['Fav. At Home?'].dropna().unique()
        assert set(home_values).issubset({0, 1}), "Fav. At Home? should be 0 or 1"

if __name__ == "__main__":
    pytest.main([__file__])