"""
Migration Script: Convert Historical Dashes to Zeros
Version 2.0 - Philosophical Shift Migration

This script converts all '-' (dash) values to '0' in the observations table
to align historical data with the new v2.0 philosophy: Absence = Zero Engagement

SAFETY FEATURES:
- Backs up all observations to CSV before any changes
- Shows counts and asks for confirmation
- Generates detailed before/after report
- Can be run multiple times safely (idempotent)

USAGE:
1. Run this script from the engagement_tracker directory
2. Review the counts shown
3. Confirm to proceed with migration
4. Check the generated backup and report files
"""

import os
import sys
from datetime import datetime
import pandas as pd

# Add parent directory to path to import database module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import database as db
except ImportError:
    print("❌ Error: Could not import database module")
    print("Make sure you're running this from the engagement_tracker directory")
    sys.exit(1)


def export_backup():
    """Export all observations to CSV backup"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'observations_backup_{timestamp}.csv'
    
    print("\n" + "="*70)
    print("📦 STEP 1: BACKING UP CURRENT DATA")
    print("="*70)
    
    try:
        observations_df = db.load_observations()
        
        if len(observations_df) == 0:
            print("⚠️  No observations found in database")
            return None, 0
        
        observations_df.to_csv(backup_file, index=False)
        
        print(f"✅ Backup created: {backup_file}")
        print(f"   Total observations: {len(observations_df)}")
        
        return backup_file, len(observations_df)
        
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return None, 0


def count_dashes():
    """Count how many dash values exist"""
    print("\n" + "="*70)
    print("🔍 STEP 2: ANALYZING CURRENT DATA")
    print("="*70)
    
    try:
        observations_df = db.load_observations()
        
        total_obs = len(observations_df)
        dash_count = len(observations_df[observations_df['value'] == '-'])
        zero_count = len(observations_df[observations_df['value'] == '0'])
        one_count = len(observations_df[observations_df['value'] == '1'])
        
        print(f"\n📊 Current Value Distribution:")
        print(f"   Total observations: {total_obs}")
        print(f"   1s (Observed):      {one_count:,} ({one_count/total_obs*100:.1f}%)")
        print(f"   0s (Not Observed):  {zero_count:,} ({zero_count/total_obs*100:.1f}%)")
        print(f"   - (Dashes):         {dash_count:,} ({dash_count/total_obs*100:.1f}%)")
        
        # Calculate affected students and days
        dash_obs = observations_df[observations_df['value'] == '-']
        affected_students = dash_obs['student_id'].nunique()
        affected_days = dash_obs['date'].nunique()
        
        print(f"\n👥 Impact Analysis:")
        print(f"   Students with dashes: {affected_students}")
        print(f"   Days with dashes:     {affected_days}")
        
        return dash_count, affected_students, affected_days
        
    except Exception as e:
        print(f"❌ Error analyzing data: {e}")
        return 0, 0, 0


def convert_dashes_to_zeros():
    """Convert all dash values to zeros in the database"""
    print("\n" + "="*70)
    print("🔄 STEP 3: CONVERTING DASHES TO ZEROS")
    print("="*70)
    
    try:
        # Get database connection
        engine = db.get_database_connection()
        
        if engine is None:
            print("❌ Could not connect to database")
            return 0, 0
        
        print("   Connected to Neon database...")
        
        with engine.connect() as conn:
            # Count before
            result = conn.execute(db.text("SELECT COUNT(*) FROM observations WHERE value = '-'"))
            before_count = result.scalar()
            
            print(f"   Found {before_count:,} dash values to convert")
            
            # Update all dashes to zeros
            print("   Executing UPDATE query...")
            conn.execute(db.text("UPDATE observations SET value = '0' WHERE value = '-'"))
            conn.commit()
            
            # Count after
            result = conn.execute(db.text("SELECT COUNT(*) FROM observations WHERE value = '-'"))
            after_count = result.scalar()
            
            result = conn.execute(db.text("SELECT COUNT(*) FROM observations WHERE value = '0'"))
            zero_count = result.scalar()
            
            print(f"\n✅ Conversion complete!")
            print(f"   Dashes remaining:  {after_count}")
            print(f"   Total zeros now:   {zero_count:,}")
            print(f"   Records updated:   {before_count:,}")
            
            return before_count, after_count
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0


def generate_report(backup_file, dash_count, affected_students, affected_days, converted):
    """Generate migration report"""
    print("\n" + "="*70)
    print("📋 STEP 4: GENERATING MIGRATION REPORT")
    print("="*70)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f'migration_report_{timestamp}.txt'
    
    report_content = f"""
================================================================================
ENGAGEMENT TRACKER v2.0 - MIGRATION REPORT
================================================================================

Migration Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Database: Neon.tech PostgreSQL

================================================================================
BACKUP INFORMATION
================================================================================

Backup File: {backup_file}
Status: Created successfully

================================================================================
BEFORE MIGRATION
================================================================================

Total observations with dashes (-): {dash_count:,}
Students affected: {affected_students}
Days affected: {affected_days}

================================================================================
MIGRATION PERFORMED
================================================================================

Action: UPDATE observations SET value = '0' WHERE value = '-'
Records updated: {converted:,}

================================================================================
AFTER MIGRATION
================================================================================

Dashes remaining: 0 (all converted to zeros)
Status: ✅ SUCCESSFUL

================================================================================
PHILOSOPHICAL CHANGE
================================================================================

OLD BEHAVIOR:
- Dash (-) = Absent, ignored in achievement calculations
- Achievement % = Performance when present only

NEW BEHAVIOR:
- Zero (0) = Absent, counted in achievement calculations
- Achievement % = Performance across ALL days (present + absent)
- Dash (-) reserved for "didn't apply that day" only

IMPACT:
- Students with poor attendance will now have lower achievement scores
- This aligns with v2.0 philosophy: Absence = Zero Engagement
- All data now consistent and comparable

================================================================================
NEXT STEPS
================================================================================

1. ✅ Backup created and saved
2. ✅ All dashes converted to zeros
3. ⚠️  Keep backup file safe for reference
4. 🔄 Refresh dashboards to see updated scores
5. 📊 Review student achievement scores (will be lower for absent students)

================================================================================
NOTES
================================================================================

- This migration is PERMANENT (dashes converted to zeros in database)
- Backup file can be used to restore if needed
- Achievement scores will be lower for students with poor attendance
- This is INTENTIONAL and reflects the new v2.0 philosophy

================================================================================
"""
    
    with open(report_file, 'w') as f:
        f.write(report_content)
    
    print(f"✅ Report saved: {report_file}")
    print("\n" + "="*70)
    print("🎉 MIGRATION COMPLETE!")
    print("="*70)
    print(f"\n📁 Files created:")
    print(f"   - {backup_file} (backup)")
    print(f"   - {report_file} (report)")
    
    return report_file


def main():
    """Main migration process"""
    print("\n" + "="*70)
    print("🚀 ENGAGEMENT TRACKER v2.0 - DATA MIGRATION")
    print("="*70)
    print("\nThis script will convert all dash (-) values to zero (0) values")
    print("to align with the new v2.0 philosophy: Absence = Zero Engagement")
    print("\n⚠️  This is a PERMANENT change to the database")
    print("   (but we'll create a backup first)")
    
    # Step 1: Backup
    backup_file, total_obs = export_backup()
    
    if backup_file is None:
        print("\n❌ Cannot proceed without backup. Exiting.")
        return
    
    # Step 2: Count dashes
    dash_count, affected_students, affected_days = count_dashes()
    
    if dash_count == 0:
        print("\n✅ No dashes found - database already migrated!")
        print("   Nothing to do.")
        return
    
    # Step 3: Confirm
    print("\n" + "="*70)
    print("⚠️  CONFIRMATION REQUIRED")
    print("="*70)
    print(f"\nReady to convert {dash_count:,} dash values to zeros")
    print(f"This will affect {affected_students} students across {affected_days} days")
    
    response = input("\n❓ Proceed with migration? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\n❌ Migration cancelled. No changes made.")
        print(f"   Backup file preserved: {backup_file}")
        return
    
    # Step 4: Convert
    converted, remaining = convert_dashes_to_zeros()
    
    if remaining > 0:
        print(f"\n⚠️  Warning: {remaining} dashes still remain")
        print("   Migration may have failed. Check the database.")
        return
    
    # Step 5: Report
    report_file = generate_report(backup_file, dash_count, affected_students, affected_days, converted)
    
    print("\n" + "="*70)
    print("✅ ALL DONE!")
    print("="*70)
    print("\nYour data has been successfully migrated to v2.0")
    print("Achievement scores now reflect total engagement (attending + participating)")
    print("\n💡 Tip: Refresh your Streamlit app to see the updated scores")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Migration interrupted by user")
        print("   No changes were made (if conversion hadn't started)")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        print("   Check the error message and try again")
