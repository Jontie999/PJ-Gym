#!/usr/bin/env python3
"""
Data cleanup script for PJ-Gym workout logs.
Enhanced version with detailed logging to identify exact outliers.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Read the CSV file, skip the comment header lines
df = pd.read_csv('workout_detailed_exercise_logs.csv', skiprows=7)

# Parse the date column
def extract_date(date_str):
    try:
        parts = str(date_str).split()
        if len(parts) >= 3:
            month_str = parts[1]
            day_str = parts[2]
            year_str = parts[3]
            return pd.to_datetime(f"{year_str} {month_str} {day_str}")
    except:
        pass
    return pd.NaT

df['parsed_date'] = df['date'].apply(extract_date)

# Calculate volume for each entry (sets * reps * weight)
df['volume'] = df['sets'] * df['reps'] * df['weight']
df['volume'] = df['volume'].fillna(0)

print("=" * 80)
print("PJ-GYM DATA CLEANUP - DETAILED ANALYSIS")
print("=" * 80)

# Show entries with zero weight (most likely errors)
zero_weight = df[(df['weight'] == 0.00) & (df['sets'] > 0)]
print(f"\nENTRIES WITH ZERO WEIGHT (but non-zero sets): {len(zero_weight)}")
if len(zero_weight) > 0:
    for idx, row in zero_weight.iterrows():
        print(f"  {row['parsed_date'].strftime('%Y-%m-%d')} - {row['exercise_name']}: {int(row['sets'])} sets x {int(row['reps'])} reps x 0.00 weight")

# Show entries with zero sets/reps (incomplete entries)
incomplete = df[((df['sets'] == 0) | (pd.isna(df['sets']))) & (df['reps'].notna())]
print(f"\nINCOMPLETE ENTRIES (zero/missing sets): {len(incomplete)}")
if len(incomplete) > 0:
    for idx, row in incomplete.iterrows():
        print(f"  {row['parsed_date'].strftime('%Y-%m-%d')} - {row['exercise_name']}: sets={row['sets']}, reps={row['reps']}, weight={row['weight']}")

# Find the days with the highest total volume
daily_volumes = df.groupby('parsed_date').agg({
    'volume': 'sum',
    'id': 'count'
}).reset_index()
daily_volumes.columns = ['date', 'total_volume', 'entry_count']
daily_volumes = daily_volumes.sort_values('total_volume', ascending=False)

print("\n" + "=" * 80)
print("TOP 10 DAYS BY TOTAL VOLUME")
print("=" * 80)
for idx, row in daily_volumes.head(10).iterrows():
    print(f"{row['date'].strftime('%Y-%m-%d (%A)')}: {row['total_volume']:.2f} volume ({int(row['entry_count'])} entries)")

# Get the 4 largest days
top_4_days = daily_volumes.head(4)['date'].tolist()

print("\n" + "=" * 80)
print("DETAILED LOOK AT THE 4 LARGEST DAYS")
print("=" * 80)

for day_num, day in enumerate(top_4_days, 1):
    day_entries = df[df['parsed_date'] == day].sort_values('exercise_name')
    day_volume = day_entries['volume'].sum()
    
    print(f"\n{day_num}. {day.strftime('%A, %B %d, %Y')}")
    print(f"   Total Volume: {day_volume:.2f}")
    print(f"   Entries:")
    
    for _, entry in day_entries.iterrows():
        vol = entry['volume']
        print(f"     • {entry['exercise_name']}: {int(entry['sets'])}x{int(entry['reps'])}x{entry['weight']:.2f} = {vol:.2f}")
    
    # Check previous week
    prev_week = day - timedelta(days=7)
    prev_entries = df[df['parsed_date'] == prev_week]
    prev_volume = prev_entries['volume'].sum()
    
    print(f"\n   Previous Week ({prev_week.strftime('%B %d')}): {prev_volume:.2f} volume")
    if len(prev_entries) > 0:
        print(f"   Entries:")
        for _, entry in prev_entries.iterrows():
            vol = entry['volume']
            print(f"     • {entry['exercise_name']}: {int(entry['sets'])}x{int(entry['reps'])}x{entry['weight']:.2f} = {vol:.2f}")

print("\n" + "=" * 80)
print("Analysis complete. Check which entries should be corrected.")
print("=" * 80)
