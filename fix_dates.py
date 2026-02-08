"""
Fix date formats in existing observations.csv file
Run this if you get date parsing errors
"""

import pandas as pd
import os

DATA_FILE = 'data/observations.csv'

if os.path.exists(DATA_FILE):
    print("Fixing date formats in observations.csv...")
    
    # Read the file
    df = pd.read_csv(DATA_FILE, dtype={'student_id': str})
    
    print(f"Found {len(df)} observations")
    
    # Convert dates to consistent format
    try:
        df['date'] = pd.to_datetime(df['date'], format='ISO8601')
    except:
        try:
            df['date'] = pd.to_datetime(df['date'], format='mixed')
        except:
            df['date'] = pd.to_datetime(df['date'])
    
    # Save with consistent format (YYYY-MM-DD)
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    
    # Backup original
    if os.path.exists(DATA_FILE + '.backup'):
        os.remove(DATA_FILE + '.backup')
    
    import shutil
    shutil.copy(DATA_FILE, DATA_FILE + '.backup')
    print(f"Created backup: {DATA_FILE}.backup")
    
    # Save fixed version
    df.to_csv(DATA_FILE, index=False)
    
    print(f"✅ Fixed {len(df)} observations")
    print(f"All dates now in YYYY-MM-DD format")
    print(f"Original file backed up to: {DATA_FILE}.backup")
    
else:
    print(f"No file found at {DATA_FILE}")
    print("Nothing to fix!")
