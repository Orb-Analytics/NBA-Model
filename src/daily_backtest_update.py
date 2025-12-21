#!/usr/bin/env python3
"""
Daily Backtest Update - Ensures All Games Are Included
Author: Orb Analytics (Liam Chaitin)
Purpose: Run daily to regenerate unified results and backtest with latest data
         Automatically detects the latest date and ensures no games are missed
"""

import sys
import subprocess
from datetime import datetime


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*100}")
    print(f"🔄 {description}")
    print(f"{'='*100}\n")
    
    result = subprocess.run(command, shell=True, capture_output=False, text=True)
    
    if result.returncode != 0:
        print(f"\n❌ {description} failed with return code {result.returncode}")
        return False
    
    print(f"\n✅ {description} completed successfully")
    return True


def main():
    """Run the complete daily update process."""
    
    print("\n" + "="*100)
    print("🔄 DAILY BACKTEST UPDATE")
    print("="*100)
    print(f"📅 Run Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*100)
    
    # Step 1: Regenerate unified results (auto-detects latest date)
    step1 = run_command(
        "python src/regenerate_unified_results.py",
        "Step 1: Regenerate Unified Model Results"
    )
    
    if not step1:
        print("\n⚠️  Unified results regeneration failed. Stopping.")
        sys.exit(1)
    
    # Step 2: Run backtest (auto-detects latest date)
    step2 = run_command(
        "python src/backtest_averaged_simple.py",
        "Step 2: Run Averaged Model Backtest"
    )
    
    if not step2:
        print("\n⚠️  Backtest failed. Stopping.")
        sys.exit(1)
    
    # Step 3: Update BACKTEST_RESULTS.md
    step3 = run_command(
        "python src/update_backtest_results_md.py",
        "Step 3: Update BACKTEST_RESULTS.md"
    )
    
    if not step3:
        print("\n⚠️  Markdown update failed. Stopping.")
        sys.exit(1)
    
    # Step 4: Verify files were updated
    print("\n" + "="*100)
    print("✅ DAILY UPDATE COMPLETE")
    print("="*100)
    print("\n📊 Updated Files:")
    print("  - data/unified_model_results.csv")
    print("  - data/averaged_model_backtest.csv")
    print("  - data/averaged_model_predictions_history.csv")
    print("  - BACKTEST_RESULTS.md")
    print("\n🎯 Next Steps:")
    print("  - Commit changes to git")
    print("  - Generate today's predictions")
    print("  - Send email notifications")
    print("="*100)


if __name__ == "__main__":
    main()
