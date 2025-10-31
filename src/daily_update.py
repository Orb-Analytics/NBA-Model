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

    # 1️⃣ Fetch today's Novig odds
    run_script("src/novig_nba_odds.py")

    # 1.5️⃣ Merge Novig odds into master
    run_script("src/merge_novig_odds.py")

    # 2️⃣ Fetch yesterday’s ESPN scores
    run_script("src/update_nba_data.py")

    # 3️⃣ Merge raw sheet (latest file in /data/raw)
    run_script("src/merge_nba_scores.py")

    print(f"\n🎯 Daily NBA Data Pipeline Complete — {today}\n")

    # 4️⃣ Commit + Push
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