import pandas as pd
from pathlib import Path

def validate_master_dataset():
    """Validate the master NBA training set for data quality."""
    master_file = Path("data/NBA Training Set 25-26.csv")

    if not master_file.exists():
        print("❌ Master file not found")
        return False

    df = pd.read_csv(master_file)
    print(f"📂 Validating {len(df)} rows from {master_file}")

    issues = []

    # 1. No nulls in critical columns
    critical_cols = ['Date', 'Favorite', 'Underdog', 'Spread']
    for col in critical_cols:
        if col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                issues.append(f"❌ {null_count} null values in {col}")
            else:
                print(f"✅ No nulls in {col}")

    # 2. Validate odds range (−10000 to +10000)
    odds_cols = ['Fav. Odds', 'Dog Odds']
    for col in odds_cols:
        if col in df.columns:
            invalid_odds = df[~df[col].between(-10000, 10000, inclusive='both')]
            if not invalid_odds.empty:
                issues.append(f"❌ {len(invalid_odds)} invalid odds in {col}")
            else:
                print(f"✅ {col} values within valid range")

    # 3. Validate Fav. At Home? = {0, 1}
    if 'Fav. At Home?' in df.columns:
        invalid_home = df[~df['Fav. At Home?'].isin([0, 1])]
        if not invalid_home.empty:
            issues.append(f"❌ {len(invalid_home)} invalid Fav. At Home? values")
        else:
            print("✅ Fav. At Home? values are valid (0 or 1)")

    # 4. Check data types
    expected_numeric = ['Spread', 'Fav. At Home?', 'Favorite Score', 'Underdog Score',
                       'Favorite - Underdog (+/-)', 'Favorite Cover?', 'Favorite Win?',
                       'Away Score', 'Home Score', 'Home/Away +/-', 'Fav. Odds', 'Dog Odds']

    for col in expected_numeric:
        if col in df.columns:
            try:
                pd.to_numeric(df[col], errors='coerce')
                print(f"✅ {col} is numeric")
            except Exception as e:
                issues.append(f"❌ {col} contains non-numeric values: {e}")

    # 5. Check for reasonable spread values
    if 'Spread' in df.columns:
        extreme_spreads = df[df['Spread'].abs() > 50]
        if not extreme_spreads.empty:
            print(f"⚠️ {len(extreme_spreads)} games with spreads > 50 (may be valid)")

    if issues:
        print("\n🚨 Validation Issues:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("\n🎉 All validations passed!")
        return True

if __name__ == "__main__":
    validate_master_dataset()