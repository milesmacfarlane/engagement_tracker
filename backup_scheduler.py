import database as db
import pandas as pd
from datetime import datetime
import os

def daily_backup():
    """Export all data to timestamped CSV files"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Load all data
    students = db.load_students()
    classes = db.load_classes()
    observations = db.load_observations()
    
    # Save to timestamped files
    students.to_csv(f'backups/students_{timestamp}.csv', index=False)
    classes.to_csv(f'backups/classes_{timestamp}.csv', index=False)
    observations.to_csv(f'backups/observations_{timestamp}.csv', index=False)
    
    print(f"✅ Backup created: {timestamp}")

if __name__ == "__main__":
    daily_backup()
