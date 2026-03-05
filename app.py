"""
Student Engagement Tracking System
Main Streamlit Application

A comprehensive tool for tracking and analyzing student behavioral engagement
across 9 key measures using a 1/0/- observation system.
"""

import streamlit as st
import sys
from pathlib import Path
from sqlalchemy import text

# Import database module first to initialize tables
import database as db

# Initialize database tables on app startup (if not already initialized)
if 'db_initialized' not in st.session_state:
    try:
        # Check if initialize_database function exists
        if hasattr(db, 'initialize_database'):
            db.initialize_database()
            st.session_state.db_initialized = True
        else:
            # Database module doesn't have initialize_database
            # Tables will be created on first use
            st.session_state.db_initialized = True
    except Exception as e:
        st.warning(f"Database initialization skipped: {str(e)}")
        st.session_state.db_initialized = False

# Import page modules
import entry_log
import student_dashboard
import class_dashboard
import reports
import setup

# Configure page
st.set_page_config(
    page_title="Student Engagement Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1F4788;
        margin-bottom: 0.5rem;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 5px;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #f0f2f6;
    }
    
    /* Table styling */
    .dataframe {
        font-size: 0.9rem;
    }
    
    /* Success box */
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    /* Info box */
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 4px solid #0c5460;
        border-radius: 4px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application logic"""
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/1F4788/FFFFFF?text=Engagement+Tracker", 
                use_container_width=True)
        
        st.markdown("---")
        
        # Database health check
        try:
            engine = db.get_database_connection()
            if engine:
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT 1"))
                    st.success("🟢 Database Online", icon="✅")
            else:
                st.error("🔴 Database Offline", icon="❌")
        except Exception as e:
            st.error("🔴 DB Connection Issue", icon="⚠️")
            with st.expander("Error Details"):
                st.code(str(e))
        
        st.markdown("---")
        
        # Navigation menu
        page = st.radio(
            "Navigate",
            options=[
                "📝 Quick Entry Log",
                "👤 Student Dashboard",
                "📚 Class Dashboard",
                "📄 Reports",
                "⚙️ Setup"
            ],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Quick stats in sidebar
        students_df = db.load_students()
        classes_df = db.load_classes()
        observations_df = db.load_observations()
        
        st.markdown("### 📊 Quick Stats")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Students", len(students_df))
        with col2:
            st.metric("Classes", len(classes_df))
        
        st.metric("Total Observations", len(observations_df))
        
        st.markdown("---")
        
        # TEMPORARY: Migration button for v2.0
        st.markdown("### 🔧 Admin Tools")
        st.caption("v2.0 Migration")
        
        if st.button("🔄 Migrate Dashes → Zeros", help="Convert all dash (-) values to zeros (0) for v2.0 philosophy"):
            st.markdown("---")
            st.warning("⚠️ **Running Migration Script**")
            st.info("This will convert all dash (-) values to zeros (0) in the database.")
            
            try:
                import subprocess
                import sys
                
                # Run the migration script
                result = subprocess.run(
                    [sys.executable, 'migrate_dashes_to_zeros.py'],
                    capture_output=True,
                    text=True,
                    timeout=120  # 2 minute timeout
                )
                
                # Display output
                if result.stdout:
                    st.text_area("Migration Output", result.stdout, height=400)
                
                if result.returncode == 0:
                    st.success("✅ Migration completed successfully!")
                    st.info("Please refresh the page to see updated scores.")
                else:
                    st.error("❌ Migration failed")
                    if result.stderr:
                        st.text_area("Error Details", result.stderr, height=200)
                        
            except subprocess.TimeoutExpired:
                st.error("❌ Migration timed out (took longer than 2 minutes)")
            except FileNotFoundError:
                st.error("❌ Migration script not found. Make sure 'migrate_dashes_to_zeros.py' is uploaded to GitHub.")
            except Exception as e:
                st.error(f"❌ Error running migration: {str(e)}")
        
        st.markdown("---")
        
        # Help section
        with st.expander("ℹ️ About"):
            st.markdown("""
            **Student Engagement Tracker**
            
            Track and analyze student behavioral 
            engagement across 9 key measures.
            
            **Version:** 1.0
            
            **System:**
            - 1 = Observed
            - 0 = Not Observed  
            - \- = Absent
            """)
        
        # Footer
        st.markdown("---")
        st.caption("© 2024 Student Engagement Tracker")
    
    # Main content area - route to selected page
    if page == "📝 Quick Entry Log":
        entry_log.render()
    
    elif page == "👤 Student Dashboard":
        student_dashboard.render()
    
    elif page == "📚 Class Dashboard":
        class_dashboard.render()
    
    elif page == "📄 Reports":
        reports.render()
    
    elif page == "⚙️ Setup":
        setup.render()


if __name__ == "__main__":
    main()
