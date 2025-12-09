"""
Run all four models for backtesting
"""

import subprocess
import sys

models = [
    ('Logistic Regression', 'python3 src/logistic_spread_model.py'),
    ('Linear Regression', 'python3 src/linear_spread_model.py'),
    ('Random Forest', 'python3 src/random_forest_spread_model.py'),
    ('Decision Tree', 'python3 src/decision_tree_spread_model.py')
]

print("\n" + "="*80)
print("🚀 RUNNING ALL FOUR MODELS")
print("="*80)

for model_name, command in models:
    print(f"\n▶️  Running {model_name}...")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"❌ {model_name} failed with return code {result.returncode}")
        sys.exit(1)

print("\n" + "="*80)
print("✅ ALL MODELS COMPLETED SUCCESSFULLY")
print("="*80)
print("\nGenerated files:")
print("  📄 data/logistic_model_results.csv")
print("  📄 data/linear_model_results.csv")
print("  📄 data/random_forest_model_results.csv")
print("  📄 data/decision_tree_model_results.csv")
