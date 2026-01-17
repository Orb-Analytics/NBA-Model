"""
Daily NBA Data Update Pipeline
Author: Orb Analytics (Liam Chaitin)
Purpose: Orchestrate full daily ETL (Novig odds, ESPN scores, raw sheet merge)
"""

import subprocess
import sys
from datetime import datetime

def run_script(script_path):
    print(f"🚀 Running {script_path} ...")
    try:
        subprocess.run(["python", script_path], check=True)
        print(f"✅ Completed: {script_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {script_path}: {e}")
        sys.exit(1)

def main():
    print("\n🏀 Starting Daily NBA Data Pipeline...\n")
    today = datetime.now().strftime("%Y-%m-%d")

    # 1️⃣ Merge raw training data (exported from Google Sheets)
    run_script("src/merge_raw_data.py")

    # 2️⃣ Normalize and clean master dataset
    run_script("src/normalize_data.py")

    # 3️⃣ Fetch today's Novig odds
    run_script("src/novig_nba_odds.py")

    # 4️⃣ Merge Novig odds into master
    run_script("src/merge_novig_odds.py")

    # 5️⃣ Fetch yesterday's ESPN scores
    run_script("src/update_nba_data.py")

    # 6️⃣ Merge scores into master
    run_script("src/merge_nba_scores.py")

    # 7️⃣ Validate data integrity
    run_script("src/validate_data.py")

    # 8️⃣ Verify score consistency (prevent home/away score mismatches)
    print("🔍 Verifying score consistency...")
    result = subprocess.run(["python", "src/verify_scores_match_home_away.py"], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print("⚠️  Score mismatches detected!")
        print(result.stdout)
        print("Attempting to auto-fix...")
        subprocess.run(["python", "src/fix_all_score_mismatches.py"], check=True)
        print("✅ Scores fixed!")
    else:
        print("✅ All scores consistent")

    print(f"\n🎯 Daily NBA Data Pipeline Complete — {today}\n")

    # 8️⃣ Commit + Push
    try:
        subprocess.run(["git", "add", "."], check=True)
        commit_msg = f"🏀 NBA Auto-Update: {today}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Successfully pushed updates to GitHub.")
    except Exception as e:
        print(f"⚠️ Git push failed: {e}")

if __name__ == "__main__":
    main()