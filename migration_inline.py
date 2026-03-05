"""
Inline Migration Functions for Streamlit App
Converts dashes to zeros directly without subprocess
"""

import pandas as pd
from datetime import datetime
from sqlalchemy import text


def run_migration_inline(db_module, st):
    """
    Run migration inline within Streamlit app
    
    Args:
        db_module: The database module
        st: Streamlit module
    """
    
    st.markdown("---")
    st.markdown("### 📦 STEP 1: Backing Up Data")
    
    # Backup
    try:
        observations_df = db_module.load_observations()
        
        if len(observations_df) == 0:
            st.warning("⚠️ No observations found in database")
            return False
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'observations_backup_{timestamp}.csv'
        
        # Save to downloadable file
        csv = observations_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Backup CSV",
            data=csv,
            file_name=backup_file,
            mime='text/csv'
        )
        
        st.success(f"✅ Backup ready: {len(observations_df)} observations")
        
    except Exception as e:
        st.error(f"❌ Error creating backup: {e}")
        return False
    
    st.markdown("---")
    st.markdown("### 🔍 STEP 2: Analyzing Current Data")
    
    # Count dashes
    total_obs = len(observations_df)
    dash_count = len(observations_df[observations_df['value'] == '-'])
    zero_count = len(observations_df[observations_df['value'] == '0'])
    one_count = len(observations_df[observations_df['value'] == '1'])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total", f"{total_obs:,}")
    with col2:
        st.metric("1s", f"{one_count:,}", f"{one_count/total_obs*100:.1f}%")
    with col3:
        st.metric("0s", f"{zero_count:,}", f"{zero_count/total_obs*100:.1f}%")
    with col4:
        st.metric("Dashes", f"{dash_count:,}", f"{dash_count/total_obs*100:.1f}%")
    
    if dash_count == 0:
        st.success("✅ No dashes found - database already migrated!")
        return True
    
    # Calculate affected students and days
    dash_obs = observations_df[observations_df['value'] == '-']
    affected_students = dash_obs['student_id'].nunique()
    affected_days = dash_obs['date'].nunique()
    
    st.info(f"""
    **Impact Analysis:**
    - Students with dashes: {affected_students}
    - Days with dashes: {affected_days}
    - Total dashes to convert: {dash_count:,}
    """)
    
    st.markdown("---")
    st.markdown("### ⚠️ CONFIRMATION REQUIRED")
    
    st.warning(f"""
    **Ready to convert {dash_count:,} dash values to zeros**
    
    This will:
    - Change all '-' to '0' in the database
    - Make achievement scores lower for absent students
    - Align all data with v2.0 philosophy
    
    **This is PERMANENT!** (But you have the backup above)
    """)
    
    # Confirmation
    confirmed = st.checkbox("✅ I understand and want to proceed with the migration")
    
    if not confirmed:
        st.info("👆 Check the box above to proceed")
        return False
    
    if st.button("🚀 RUN MIGRATION NOW", type="primary"):
        st.markdown("---")
        st.markdown("### 🔄 STEP 3: Converting Dashes to Zeros")
        
        progress_bar = st.progress(0)
        status = st.empty()
        
        try:
            # Get database connection
            engine = db_module.get_database_connection()
            
            if engine is None:
                st.error("❌ Could not connect to database")
                return False
            
            status.text("Connecting to database...")
            progress_bar.progress(25)
            
            with engine.connect() as conn:
                # Count before
                result = conn.execute(text("SELECT COUNT(*) FROM observations WHERE value = '-'"))
                before_count = result.scalar()
                
                status.text(f"Found {before_count:,} dashes to convert...")
                progress_bar.progress(50)
                
                # Update
                status.text("Executing UPDATE query...")
                conn.execute(text("UPDATE observations SET value = '0' WHERE value = '-'"))
                conn.commit()
                
                progress_bar.progress(75)
                
                # Count after
                result = conn.execute(text("SELECT COUNT(*) FROM observations WHERE value = '-'"))
                after_count = result.scalar()
                
                result = conn.execute(text("SELECT COUNT(*) FROM observations WHERE value = '0'"))
                zero_count_after = result.scalar()
                
                progress_bar.progress(100)
                status.text("Complete!")
                
                st.markdown("---")
                st.markdown("### ✅ MIGRATION COMPLETE!")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Records Updated", f"{before_count:,}")
                with col2:
                    st.metric("Dashes Remaining", after_count)
                with col3:
                    st.metric("Total Zeros Now", f"{zero_count_after:,}")
                
                if after_count == 0:
                    st.success("""
                    🎉 **Success!** All dashes converted to zeros.
                    
                    **Next Steps:**
                    1. Refresh this page (Ctrl+Shift+R)
                    2. Check Student Dashboard for updated scores
                    3. Achievement % will be lower for absent students (expected!)
                    """)
                    
                    # Create report
                    report = f"""
================================================================================
ENGAGEMENT TRACKER v2.0 - MIGRATION REPORT
================================================================================

Migration Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Database: Neon.tech PostgreSQL

BEFORE MIGRATION:
- Total observations with dashes: {before_count:,}
- Students affected: {affected_students}
- Days affected: {affected_days}

MIGRATION PERFORMED:
- Action: UPDATE observations SET value = '0' WHERE value = '-'
- Records updated: {before_count:,}

AFTER MIGRATION:
- Dashes remaining: {after_count}
- Total zeros: {zero_count_after:,}
- Status: ✅ SUCCESSFUL

PHILOSOPHICAL CHANGE:
- OLD: Dash (-) = Absent, ignored in calculations
- NEW: Zero (0) = Absent, counted in calculations
- Impact: Students with poor attendance now have lower achievement scores
================================================================================
"""
                    
                    st.download_button(
                        label="📄 Download Migration Report",
                        data=report,
                        file_name=f'migration_report_{timestamp}.txt',
                        mime='text/plain'
                    )
                    
                    return True
                else:
                    st.warning(f"⚠️ {after_count} dashes still remain. Migration may have failed.")
                    return False
                    
        except Exception as e:
            st.error(f"❌ Error during conversion: {e}")
            import traceback
            st.code(traceback.format_exc())
            return False
    
    return False
