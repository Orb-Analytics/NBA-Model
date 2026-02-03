"""
Reprocess Missing Dates from Google Sheets
---------------------------------------------
Use this script after manually re-exporting correct data from Google Sheets
for dates that had empty exports.

Usage:
    python src/reprocess_missing_dates.py 2026-02-02 2026-02-03
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime


def reprocess_date(date_str):
    """Reprocess a single date's data."""
    print(f"\n{'=' * 60}")
    print(f"🔄 Reprocessing {date_str}")
    print(f"{'=' * 60}\n")
    
    # Check if raw file exists
    raw_file = Path(f"data/raw/NBA_Training_Set_{date_str}.csv")
    if not raw_file.exists():
        print(f"❌ Raw file not found: {raw_file}")
        print("   Please export from Google Sheets first!")
        return False
    
    # Check file size
    if raw_file.stat().st_size < 1000:  # Less than 1KB suggests empty file
        print(f"⚠️  File exists but appears empty ({raw_file.stat().st_size} bytes)")
        with open(raw_file) as f:
            lines = f.readlines()
        print(f"   Lines in file: {len(lines)}")
        if len(lines) <= 1:
            print(f"❌ File only contains header - no data!")
            print("   Please re-export from Google Sheets with actual data!")
            return False
    
    print(f"✅ Raw file exists: {raw_file} ({raw_file.stat().st_size} bytes)")
    
    # Run the data pipeline steps
    steps = [
        ("Merge raw data", "src/merge_raw_data.py"),
        ("Normalize data", "src/normalize_data.py"),
        ("Merge scores", "src/merge_nba_scores.py"),
        ("Validate data", "src/validate_data.py"),
    ]
    
    for step_name, script_path in steps:
        print(f"\n📋 {step_name}...")
        try:
            result = subprocess.run(
                ["python", script_path],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"✅ {step_name} complete")
            if result.stdout:
                # Show last 5 lines of output
                lines = result.stdout.strip().split('\n')
                for line in lines[-5:]:
                    print(f"   {line}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error in {step_name}:")
            print(e.stderr)
            return False
    
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python src/reprocess_missing_dates.py YYYY-MM-DD [YYYY-MM-DD ...]")
        print("\nExample:")
        print("  python src/reprocess_missing_dates.py 2026-02-02 2026-02-03")
        sys.exit(1)
    
    dates = sys.argv[1:]
    
    print("\n" + "=" * 60)
    print("🔧 NBA Data Reprocessing Tool")
    print("=" * 60)
    print(f"\nDates to reprocess: {', '.join(dates)}")
    print("\n⚠️  PREREQUISITE: Export correct data from Google Sheets first!")
    print("   Files should be in: data/raw/NBA_Training_Set_YYYY-MM-DD.csv")
    
    input("\nPress Enter to continue or Ctrl+C to cancel...")
    
    success_count = 0
    failed_dates = []
    
    for date_str in dates:
        # Validate date format
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print(f"\n❌ Invalid date format: {date_str}")
            print("   Use YYYY-MM-DD format")
            failed_dates.append(date_str)
            continue
        
        if reprocess_date(date_str):
            success_count += 1
        else:
            failed_dates.append(date_str)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully processed: {success_count}/{len(dates)} dates")
    
    if failed_dates:
        print(f"❌ Failed dates: {', '.join(failed_dates)}")
        print("\nNext steps:")
        print("1. Re-export these dates from Google Sheets")
        print("2. Ensure files have actual data (not just headers)")
        print("3. Run this script again")
    else:
        print("\n🎉 All dates processed successfully!")
        print("\nNext steps:")
        print("1. Review: data/NBA Training Set 25-26.csv")
        print("2. Commit and push changes")
        print("3. Run predictions if needed")


if __name__ == "__main__":
    main()
