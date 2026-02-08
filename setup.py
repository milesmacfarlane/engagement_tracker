"""
Setup and Configuration Page
"""
import streamlit as st
import pandas as pd
import database as db
import utils


def render():
    """Render the Setup page"""
    
    st.title("⚙️ Setup & Configuration")
    st.markdown("Manage students, classes, and data")
    
    # Tabs for different setup sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "👥 Student Roster",
        "📚 Classes",
        "💾 Data Management",
        "❓ Help"
    ])
    
    with tab1:
        render_student_roster()
    
    with tab2:
        render_class_management()
    
    with tab3:
        render_data_management()
    
    with tab4:
        render_help()


def render_student_roster():
    """Render student roster management"""
    
    st.subheader("Student Roster Management")
    
    students_df = db.load_students()
    classes_df = db.load_classes()
    
    # Display current students
    st.markdown("### Current Students")
    
    if len(students_df) > 0:
        # Add search/filter
        search = st.text_input("🔍 Search students", placeholder="Enter name or ID...")
        
        if search:
            filtered = students_df[
                students_df['name'].str.contains(search, case=False, na=False) |
                students_df['student_id'].str.contains(search, case=False, na=False)
            ]
        else:
            filtered = students_df
        
        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True,
            column_config={
                "student_id": "Student ID",
                "name": "Name",
                "primary_class": "Primary Class"
            }
        )
        
        st.markdown(f"**Total Students:** {len(students_df)}")
    else:
        st.info("No students in roster. Add students below or load sample data.")
    
    st.markdown("---")
    
    # Add new student
    st.markdown("### Add New Student")
    
    with st.form("add_student_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_student_id = st.text_input("Student ID *", help="Unique student ID number")
            new_student_name = st.text_input("Student Name *", help="Full name")
        
        with col2:
            if len(classes_df) > 0:
                new_primary_class = st.selectbox(
                    "Primary Class *",
                    options=classes_df['class_code'].tolist(),
                    help="Student's primary/homeroom class"
                )
            else:
                st.warning("⚠️ No classes available. Please add classes first.")
                new_primary_class = None
        
        submit_student = st.form_submit_button("➕ Add Student", type="primary")
        
        if submit_student:
            if not new_student_id or not new_student_name:
                st.error("❌ Student ID and Name are required")
            elif new_primary_class is None:
                st.error("❌ Please add at least one class first")
            else:
                success = db.add_student(new_student_id, new_student_name, new_primary_class)
                if success:
                    st.success(f"✅ Added student: {new_student_name}")
                    st.rerun()
                else:
                    st.error(f"❌ Student ID {new_student_id} already exists")
    
    st.markdown("---")
    
    # Edit/Delete student
    if len(students_df) > 0:
        st.markdown("### Edit or Delete Student")
        
        col1, col2 = st.columns(2)
        
        with col1:
            student_to_modify = st.selectbox(
                "Select Student",
                options=students_df['student_id'].tolist(),
                format_func=lambda x: f"{students_df[students_df['student_id']==x]['name'].values[0]} ({x})",
                key="modify_student"
            )
        
        if student_to_modify:
            student = students_df[students_df['student_id'] == student_to_modify].iloc[0]
            
            with st.form("edit_student_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    edit_name = st.text_input("Name", value=student['name'])
                
                with col2:
                    if len(classes_df) > 0:
                        current_class_idx = classes_df['class_code'].tolist().index(student['primary_class']) if student['primary_class'] in classes_df['class_code'].values else 0
                        edit_class = st.selectbox(
                            "Primary Class",
                            options=classes_df['class_code'].tolist(),
                            index=current_class_idx
                        )
                    else:
                        edit_class = student['primary_class']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    update_button = st.form_submit_button("💾 Update Student", type="primary")
                
                with col2:
                    delete_button = st.form_submit_button("🗑️ Delete Student", type="secondary")
                
                if update_button:
                    db.update_student(student_to_modify, name=edit_name, primary_class=edit_class)
                    st.success("✅ Student updated")
                    st.rerun()
                
                if delete_button:
                    db.delete_student(student_to_modify)
                    st.success("✅ Student deleted (including all observations)")
                    st.rerun()
    
    st.markdown("---")
    
    # Bulk import
    st.markdown("### Bulk Import Students")
    st.info("Upload a CSV file with columns: student_id, name, primary_class")
    
    uploaded_file = st.file_uploader("Choose CSV file", type=['csv'], key="student_import")
    
    if uploaded_file is not None:
        try:
            import_df = pd.read_csv(uploaded_file, dtype={'student_id': str})
            
            # Validate columns
            required_cols = ['student_id', 'name', 'primary_class']
            if not all(col in import_df.columns for col in required_cols):
                st.error(f"❌ CSV must contain columns: {', '.join(required_cols)}")
            else:
                st.dataframe(import_df.head(), use_container_width=True)
                
                if st.button("✅ Import Students", type="primary"):
                    success_count = 0
                    error_count = 0
                    
                    for _, row in import_df.iterrows():
                        success = db.add_student(
                            row['student_id'],
                            row['name'],
                            row['primary_class']
                        )
                        if success:
                            success_count += 1
                        else:
                            error_count += 1
                    
                    st.success(f"✅ Imported {success_count} students ({error_count} duplicates skipped)")
                    st.rerun()
        
        except Exception as e:
            st.error(f"❌ Error reading CSV: {str(e)}")


def render_class_management():
    """Render class management"""
    
    st.subheader("Class Management")
    
    classes_df = db.load_classes()
    
    # Display current classes
    st.markdown("### Current Classes")
    
    if len(classes_df) > 0:
        st.dataframe(
            classes_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "class_code": "Class Code",
                "class_name": "Class Name"
            }
        )
        
        st.markdown(f"**Total Classes:** {len(classes_df)}")
    else:
        st.info("No classes defined. Add classes below or load sample data.")
    
    st.markdown("---")
    
    # Add new class
    st.markdown("### Add New Class")
    
    with st.form("add_class_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_class_code = st.text_input(
                "Class Code *",
                help="Short code (e.g., HIS20A)",
                placeholder="HIS20A"
            )
        
        with col2:
            new_class_name = st.text_input(
                "Class Name *",
                help="Full class name",
                placeholder="History 20 - Section A"
            )
        
        submit_class = st.form_submit_button("➕ Add Class", type="primary")
        
        if submit_class:
            if not new_class_code or not new_class_name:
                st.error("❌ Class Code and Name are required")
            else:
                success = db.add_class(new_class_code, new_class_name)
                if success:
                    st.success(f"✅ Added class: {new_class_code}")
                    st.rerun()
                else:
                    st.error(f"❌ Class code {new_class_code} already exists")
    
    st.markdown("---")
    
    # Edit/Delete class
    if len(classes_df) > 0:
        st.markdown("### Edit or Delete Class")
        
        class_to_modify = st.selectbox(
            "Select Class",
            options=classes_df['class_code'].tolist(),
            format_func=lambda x: f"{x} - {classes_df[classes_df['class_code']==x]['class_name'].values[0]}",
            key="modify_class"
        )
        
        if class_to_modify:
            class_info = classes_df[classes_df['class_code'] == class_to_modify].iloc[0]
            
            with st.form("edit_class_form"):
                edit_class_name = st.text_input("Class Name", value=class_info['class_name'])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    update_button = st.form_submit_button("💾 Update Class", type="primary")
                
                with col2:
                    delete_button = st.form_submit_button("🗑️ Delete Class", type="secondary")
                
                if update_button:
                    db.update_class(class_to_modify, edit_class_name)
                    st.success("✅ Class updated")
                    st.rerun()
                
                if delete_button:
                    db.delete_class(class_to_modify)
                    st.success("✅ Class deleted")
                    st.rerun()


def render_data_management():
    """Render data management options"""
    
    st.subheader("Data Management")
    
    # Sample data
    st.markdown("### 📋 Sample Data")
    st.info("""
    Load sample data to explore the system. This includes:
    - 3 classes (HIS20A, HIS20B, SST20)
    - 60-70 students
    - 10 observation sessions
    """)
    
    if st.button("🎲 Load Sample Data", type="primary"):
        db.initialize_sample_data()
        st.success("✅ Sample data loaded successfully!")
        st.balloons()
        st.rerun()
    
    st.markdown("---")
    
    # Export data
    st.markdown("### 📤 Export Data")
    st.info("Download all data as CSV files")
    
    students_df = db.load_students()
    classes_df = db.load_classes()
    observations_df = db.load_observations()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if len(students_df) > 0:
            csv = students_df.to_csv(index=False)
            st.download_button(
                "📥 Students",
                data=csv,
                file_name="students.csv",
                mime="text/csv"
            )
    
    with col2:
        if len(classes_df) > 0:
            csv = classes_df.to_csv(index=False)
            st.download_button(
                "📥 Classes",
                data=csv,
                file_name="classes.csv",
                mime="text/csv"
            )
    
    with col3:
        if len(observations_df) > 0:
            csv = observations_df.to_csv(index=False)
            st.download_button(
                "📥 Observations",
                data=csv,
                file_name="observations.csv",
                mime="text/csv"
            )
    
    st.markdown("---")
    
    # Clear data
    st.markdown("### 🗑️ Clear All Data")
    st.warning("⚠️ This will delete ALL students, classes, and observations. This cannot be undone!")
    
    if st.button("🗑️ Clear All Data", type="secondary"):
        # Save empty dataframes
        db.save_students(pd.DataFrame(columns=['student_id', 'name', 'primary_class']))
        db.save_classes(pd.DataFrame(columns=['class_code', 'class_name']))
        db.save_observations(pd.DataFrame(columns=['date', 'class_code', 'student_id', 'measure_name', 'value']))
        
        st.success("✅ All data cleared")
        st.rerun()


def render_help():
    """Render help section"""
    
    st.subheader("Help & Documentation")
    
    st.markdown("""
    ### 🎯 Quick Start Guide
    
    1. **Setup Classes**: Add your classes in the "Classes" tab
    2. **Add Students**: Import or manually add students in the "Student Roster" tab
    3. **Record Observations**: Use the "Quick Entry Log" to record daily observations
    4. **View Reports**: Check individual student performance in "Student Dashboard"
    5. **Analyze Class**: View class-wide statistics in "Class Dashboard"
    
    ### 📊 Observation System
    
    The system tracks 9 engagement behaviors using a three-value system:
    
    - **1** = Behavior was observed/demonstrated
    - **0** = Behavior was NOT observed (student present but behavior absent)
    - **-** = Student was absent or measure not applicable
    
    ### 📈 Performance Bands
    
    Student performance is classified into bands based on the percentage of observed behaviors:
    
    - **85-100%**: Exemplary
    - **75-85%**: Proficient
    - **65-75%**: Developing
    - **50-65%**: Emerging
    - **40-50%**: Beginning
    - **<40%**: Needs Intensive Support
    
    ### 🎓 The 9 Engagement Measures
    
    1. **Time on Task** - Student stays focused on assigned work
    2. **Asked/Answered/Shared** - Active participation in discussions
    3. **Work Completed/Ready** - Assignments completed and prepared
    4. **Materials/Organized** - Has necessary materials and workspace organized
    5. **Helping/Asking for Help** - Seeks or provides assistance appropriately
    6. **Asks for Clarification** - Seeks understanding when confused
    7. **Check-ins with Teacher** - Regular communication with teacher
    8. **Asks for Ways to Improve** - Seeks feedback and growth opportunities
    9. **In-class Work Completed** - Completes work during class time
    
    ### 💡 Tips for Effective Use
    
    - **Observe regularly**: Aim to observe each student at least once per week
    - **Be consistent**: Use the same criteria across all observations
    - **Focus on presence/absence**: Record what you actually observe, not potential
    - **Use the dashboard**: Review trends to identify students needing support early
    - **Export data**: Regularly back up your observations
    
    ### 🔧 Troubleshooting
    
    **Problem**: Students not appearing in entry log
    - **Solution**: Check that students are assigned to the correct class
    
    **Problem**: Performance shows as "N/A"
    - **Solution**: Ensure at least one observation with value 1 or 0 (not all -)
    
    **Problem**: Cannot delete a class
    - **Solution**: Reassign or delete students in that class first
    
    ### 📧 Support
    
    For additional help or to report issues, contact your system administrator.
    """)
