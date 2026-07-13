#!/usr/bin/env python3
"""
Data cleanup script for PJ-Gym workout logs.
Identifies 4 largest volume outliers and replaces them with previous week's average values.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict

# Read the CSV file
df = pd.read_csv('workout_detailed_exercise_logs.csv', skiprows=7)

# Convert date column to datetime
df['date'] = pd.to_datetime(df['date'])

# Calculate volume for each entry (sets * reps * weight)
df['volume'] = df['sets'] * df['reps'] * df['weight']

# Handle NaN values in volume calculation
df['volume'] = df['volume'].fillna(0)

print("=" * 80)
print("PJ-GYM WORKOUT DATA CLEANUP ANALYSIS")
print("=" * 80)

# Find entries with zero weight (potential errors)
zero_weight_entries = df[df['weight'] == 0.00]
print(f"\nEntries with zero weight: {len(zero_weight_entries)}")
print(zero_weight_entries[['date', 'exercise_name', 'sets', 'reps', 'weight', 'volume']].head(10))

# Find top 10 volume entries by date
print("\n" + "=" * 80)
print("TOP 10 LARGEST VOLUME ENTRIES")
print("=" * 80)

top_volumes = df.nlargest(10, 'volume')[['date', 'exercise_name', 'sets', 'reps', 'weight', 'volume']]
print(top_volumes.to_string())

# Identify the 4 largest outliers (group by date and sum volumes per day)
daily_volumes = df.groupby('date')['volume'].sum().reset_index()
daily_volumes.columns = ['date', 'daily_volume']
daily_volumes = daily_volumes.sort_values('daily_volume', ascending=False)

print("\n" + "=" * 80)
print("TOP WORKOUT DAYS BY TOTAL VOLUME")
print("=" * 80)
print(daily_volumes.head(10).to_string())

# Get the 4 largest days
top_4_days = daily_volumes.head(4)['date'].tolist()

print("\n" + "=" * 80)
print("4 LARGEST VOLUME DAYS TO CLEAN UP")
print("=" * 80)

for i, day in enumerate(top_4_days, 1):
    day_entries = df[df['date'] == day]
    day_volume = day_entries['volume'].sum()
    prev_week = day - timedelta(days=7)
    prev_week_entries = df[df['date'] == prev_week]
    prev_week_volume = prev_week_entries['volume'].sum()
    
    print(f"\n{i}. DATE: {day.strftime('%Y-%m-%d (%A)')}")
    print(f"   Current Volume: {day_volume:.2f}")
    print(f"   Previous Week ({prev_week.strftime('%Y-%m-%d')}): {prev_week_volume:.2f}")
    print(f"   Entries on this day: {len(day_entries)}")
    print(f"   Exercises:")
    for _, row in day_entries.iterrows():
        print(f"      - {row['exercise_name']}: {row['sets']} sets × {row['reps']} reps × {row['weight']} {row['weight_unit_label']} = {row['volume']:.2f} volume")

# Create a function to replace outlier days
def fix_outlier_days(df, top_4_days):
    """Replace outlier entries with previous week's average values"""
    df_fixed = df.copy()
    replacements = []
    
    for day in top_4_days:
        # Get entries for this day
        day_mask = df_fixed['date'] == day
        day_entries = df_fixed[day_mask]
        
        # Get previous week entries (same day of week)
        prev_week = day - timedelta(days=7)
        prev_week_mask = df_fixed['date'] == prev_week
        prev_week_entries = df_fixed[prev_week_mask]
        
        if len(prev_week_entries) > 0:
            # For each entry on the outlier day, replace with average from previous week
            for idx, (_, current_row) in enumerate(day_entries.iterrows()):
                exercise = current_row['exercise_name']
                
                # Find same exercise from previous week
                same_exercise = prev_week_entries[prev_week_entries['exercise_name'] == exercise]
                
                if len(same_exercise) > 0:
                    # Average the weight, sets, and reps from previous week
                    avg_weight = same_exercise['weight'].mean()
                    avg_sets = same_exercise['sets'].mean()
                    avg_reps = same_exercise['reps'].mean()
                    
                    # Record the replacement
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
                    
                    # Update the dataframe
                    df_fixed.loc[current_row.name, 'sets'] = int(avg_sets)
                    df_fixed.loc[current_row.name, 'reps'] = int(avg_reps)
                    df_fixed.loc[current_row.name, 'weight'] = avg_weight
    
    return df_fixed, replacements

# Generate the fixes
df_fixed, replacements = fix_outlier_days(df, top_4_days)

print("\n" + "=" * 80)
print("PROPOSED REPLACEMENTS")
print("=" * 80)

if replacements:
    for r in replacements:
        print(f"\n{r['date']} - {r['exercise']}:")
        print(f"  Sets:   {r['old_sets']} → {r['new_sets']}")
        print(f"  Reps:   {r['old_reps']} → {r['new_reps']}")
        print(f"  Weight: {r['old_weight']} → {r['new_weight']:.2f}")
else:
    print("No replacements found (exercises from previous week not available)")

# Save the cleaned data
output_file = 'workout_detailed_exercise_logs_CLEANED.csv'
print("\n" + "=" * 80)
print(f"SAVING CLEANED DATA TO: {output_file}")
print("=" * 80)

# Reconstruct the CSV with the original header
with open('workout_detailed_exercise_logs.csv', 'r') as f:
    header_lines = [f.readline() for _ in range(7)]

# Save cleaned data
df_fixed.to_csv(output_file, index=False)

print(f"\n✓ Cleaned data saved to {output_file}")
print("\nNEXT STEPS:")
print("1. Review the proposed changes above")
print("2. If satisfied, backup original: cp workout_detailed_exercise_logs.csv workout_detailed_exercise_logs.backup")
print("3. Replace original: mv workout_detailed_exercise_logs_CLEANED.csv workout_detailed_exercise_logs.csv")
print("4. Commit the changes: git add -A && git commit -m 'Data cleanup: fix 4 volume outliers'")
