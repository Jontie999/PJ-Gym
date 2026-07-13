#!/usr/bin/env python3
"""
Data cleanup script for PJ-Gym workout logs.
Identifies 4 largest volume outliers and replaces them with previous week's average values.
Executed version - produces cleaned CSV file.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Read the CSV file, skip the comment header lines
df = pd.read_csv('workout_detailed_exercise_logs.csv', skiprows=7)

# Parse the date column - extract just the date part before the time
def extract_date(date_str):
    try:
        # Format: "Wed Mar 25 2026 11:18:33 GMT+0000..."
        parts = str(date_str).split()
        if len(parts) >= 3:
            month_str = parts[1]  # Mar
            day_str = parts[2]     # 25
            year_str = parts[3]    # 2026
            # Convert to datetime
            return pd.to_datetime(f"{year_str} {month_str} {day_str}")
    except:
        pass
    return pd.NaT

df['parsed_date'] = df['date'].apply(extract_date)

# Calculate volume for each entry (sets * reps * weight)
df['volume'] = df['sets'] * df['reps'] * df['weight']
df['volume'] = df['volume'].fillna(0)

print("=" * 80)
print("PJ-GYM WORKOUT DATA CLEANUP - EXECUTING")
print("=" * 80)

# Find daily volumes
daily_volumes = df.groupby('parsed_date')['volume'].sum().reset_index()
daily_volumes.columns = ['date', 'daily_volume']
daily_volumes = daily_volumes.sort_values('daily_volume', ascending=False)

print("\nTOP 10 WORKOUT DAYS BY TOTAL VOLUME:")
print(daily_volumes.head(10).to_string())

# Get the 4 largest days
top_4_days = daily_volumes.head(4)['date'].tolist()

print("\n" + "=" * 80)
print("ANALYZING THE 4 LARGEST VOLUME DAYS:")
print("=" * 80)

for i, day in enumerate(top_4_days, 1):
    day_entries = df[df['parsed_date'] == day]
    day_volume = day_entries['volume'].sum()
    prev_week = day - timedelta(days=7)
    prev_week_entries = df[df['parsed_date'] == prev_week]
    prev_week_volume = prev_week_entries['volume'].sum()
    
    print(f"\n{i}. {day.strftime('%A, %B %d %Y')}")
    print(f"   Current Volume: {day_volume:.2f}")
    print(f"   Previous Week ({prev_week.strftime('%B %d')}): {prev_week_volume:.2f}")
    print(f"   Entries: {len(day_entries)}")

# Create the fix function
def fix_outlier_days(df, top_4_days):
    """Replace outlier entries with previous week's average values"""
    df_fixed = df.copy()
    replacements = []
    
    for day in top_4_days:
        day_mask = df_fixed['parsed_date'] == day
        day_entries = df_fixed[day_mask]
        
        prev_week = day - timedelta(days=7)
        prev_week_mask = df_fixed['parsed_date'] == prev_week
        prev_week_entries = df_fixed[prev_week_mask]
        
        if len(prev_week_entries) > 0:
            for idx, (orig_idx, current_row) in enumerate(day_entries.iterrows()):
                exercise = current_row['exercise_name']
                
                same_exercise = prev_week_entries[prev_week_entries['exercise_name'] == exercise]
                
                if len(same_exercise) > 0:
                    avg_weight = same_exercise['weight'].mean()
                    avg_sets = same_exercise['sets'].mean()
                    avg_reps = same_exercise['reps'].mean()
                    
                    replacements.append({
                        'date': day.strftime('%Y-%m-%d'),
                        'exercise': exercise,
                        'old_sets': current_row['sets'],
                        'new_sets': int(avg_sets),
                        'old_reps': current_row['reps'],
                        'new_reps': int(avg_reps),
                        'old_weight': current_row['weight'],
                        'new_weight': avg_weight,
                    })
                    
                    df_fixed.loc[orig_idx, 'sets'] = int(avg_sets)
                    df_fixed.loc[orig_idx, 'reps'] = int(avg_reps)
                    df_fixed.loc[orig_idx, 'weight'] = avg_weight
    
    return df_fixed, replacements

# Apply the fixes
df_fixed, replacements = fix_outlier_days(df, top_4_days)

print("\n" + "=" * 80)
print(f"REPLACEMENTS MADE: {len(replacements)}")
print("=" * 80)

for r in replacements:
    print(f"\n{r['date']} - {r['exercise']}:")
    print(f"  Sets:   {r['old_sets']} → {r['new_sets']}")
    print(f"  Reps:   {r['old_reps']} → {r['new_reps']}")
    print(f"  Weight: {r['old_weight']} → {r['new_weight']:.2f}")

# Save the cleaned data
output_file = 'workout_detailed_exercise_logs_CLEANED.csv'

# Reconstruct with header
header_lines = [
    "# Query: Detailed Exercise Logs (workout_detailed_exercise_logs)\n",
    "# Records: 909\n",
    "# Execution Time: 49ms\n",
    "# Category: workout\n",
    "# Generated: 2026-03-29T07:08:21.712Z\n",
    "# Contains Sensitive Data: Yes\n",
    "#\n"
]

# Drop the temporary columns and save
df_to_save = df_fixed.drop(columns=['parsed_date', 'volume'])

with open(output_file, 'w') as f:
    f.writelines(header_lines)
    df_to_save.to_csv(f, index=False)

print(f"\n✓ Cleaned data saved to {output_file}")
print("\n" + "=" * 80)
print("SUCCESS - CLEANUP COMPLETE")
print("=" * 80)
print("\nNEXT STEPS:")
print("1. Review the changes above")
print("2. Backup original: cp workout_detailed_exercise_logs.csv workout_detailed_exercise_logs.backup")
print("3. Replace: mv workout_detailed_exercise_logs_CLEANED.csv workout_detailed_exercise_logs.csv")
print("4. Commit: git add -A && git commit -m 'Data cleanup: fix 4 volume outliers'")
