"""
Quick Entry Log Page - Main data entry interface with keyboard-friendly input
"""
import streamlit as st
import pandas as pd
from datetime import date
import database as db
import utils


def render():
    """Render the Quick Entry Log page"""
    
    st.title("📝 Quick Entry Log")
    st.markdown("Record student engagement observations for your class")
    
    # Load data
    students_df = db.load_students()
    classes_df = db.load_classes()
    observations_df = db.load_observations()
    
    # Check if setup is complete
    if len(classes_df) == 0:
        st.warning("⚠️ No classes found. Please add classes in the Setup page first.")
        return
    
    if len(students_df) == 0:
        st.warning("⚠️ No students found. Please add students in the Setup page first.")
        return
    
    # Selection controls
    col1, col2 = st.columns(2)
    
    with col1:
        # More intentional date selector - no default, requires explicit selection
        # Check if date is already selected in session state
        if 'selected_observation_date' not in st.session_state:
            st.session_state.selected_observation_date = None
        
        # Date input with more prominent styling
        st.markdown("### 📅 Select Observation Date")
        st.warning("⚠️ **Important:** Select the date for these observations carefully. Existing data for this date will be overwritten.")
        
        observation_date = st.date_input(
            "Observation Date",
            value=st.session_state.selected_observation_date if st.session_state.selected_observation_date else date.today(),
            max_value=date.today(),
            help="Select the date for this observation session",
            key="obs_date_picker"
        )
        
        # Store in session state
        st.session_state.selected_observation_date = observation_date
        
        # Check if observations already exist for this date/class combination
        existing_obs = db.load_observations()
        has_existing = False
        if len(existing_obs) > 0:
            existing_mask = (pd.to_datetime(existing_obs['date']).dt.date == observation_date) & \
                           (existing_obs['class_code'] == st.session_state.get('selected_class_code', ''))
            has_existing = existing_mask.any()
            
            if has_existing:
                # Count how many students have data
                students_with_data = existing_obs[existing_mask]['student_id'].nunique()
                st.error(f"⚠️ **WARNING:** Observations already exist for this date! {students_with_data} students have data that will be OVERWRITTEN if you save.")
    
    with col2:
        st.markdown("### 👥 Select Class")
        selected_class = st.selectbox(
            "Select Class",
            options=classes_df['class_code'].tolist(),
            format_func=lambda x: f"{x} - {classes_df[classes_df['class_code']==x]['class_name'].values[0]}",
            help="Choose the class you're observing",
            key="class_selector"
        )
        
        # Store selected class in session state for the warning check above
        st.session_state.selected_class_code = selected_class
        
        # Show info about this class
        class_students_count = len(students_df[students_df['primary_class'] == selected_class])
        st.info(f"📊 {class_students_count} students in this class")
    
    # Filter students by selected class
    class_students = students_df[students_df['primary_class'] == selected_class].copy()
    
    if len(class_students) == 0:
        st.warning(f"⚠️ No students found in class {selected_class}")
        return
    
    # Calculate last observation info for each student
    class_students['last_obs_date'] = class_students['student_id'].apply(
        lambda sid: utils.get_days_since_last_observation(observations_df, sid)
    )
    
    # Sort by days since last observation (those needing observation first)
    class_students = class_students.sort_values('last_obs_date', ascending=False, na_position='first')
    
    st.markdown("---")
    st.subheader(f"Students in {selected_class} ({len(class_students)} students)")
    
    # Show recent observation dates for this class
    recent_dates = db.load_observations()
    if len(recent_dates) > 0:
        class_dates = recent_dates[recent_dates['class_code'] == selected_class]
        if len(class_dates) > 0:
            unique_dates = pd.to_datetime(class_dates['date']).dt.date.unique()
            unique_dates = sorted(unique_dates, reverse=True)[:5]  # Last 5 dates
            
            with st.expander("📅 Recent observation dates for this class", expanded=False):
                st.markdown("**Last 5 observation dates:**")
                for obs_date in unique_dates:
                    students_observed = len(class_dates[pd.to_datetime(class_dates['date']).dt.date == obs_date]['student_id'].unique())
                    date_str = obs_date.strftime('%Y-%m-%d (%A)')
                    
                    # Highlight if it's the currently selected date
                    if obs_date == observation_date:
                        st.warning(f"⚠️ **{date_str}** - {students_observed} students (CURRENTLY SELECTED - will be overwritten!)")
                    else:
                        st.info(f"✓ {date_str} - {students_observed} students")
    
    # Info box
    st.info("""
    **Entry Instructions:**
    - Select **P** (Present) or **A** (Absent) for each student
    - If PRESENT: Type **1** (observed), **0** (not observed), or **-** (not applicable) in each measure field
    - If ABSENT: All measures automatically filled with **-**
    - Press **Tab** to move to next field (auto-advances after typing)
    - Press **Enter** to move down to same measure for next student
    - Change from ABSENT to PRESENT clears the **-** values
    """)
    
    # Initialize session state for entry grid
    if 'entry_grid' not in st.session_state:
        st.session_state.entry_grid = {}
    
    if 'attendance_status' not in st.session_state:
        st.session_state.attendance_status = {}
    
    # Display entry grid with headers
    st.markdown("### Observation Entry Grid")
    
    # Measure abbreviations for column headers
    measure_abbrev = {
        "Time on Task": "Time",
        "Asked/Answered/Shared": "Ask/Ans",
        "Work Completed/Ready": "Work",
        "Materials/Organized": "Materials",
        "Helping/Asking for Help": "Help",
        "Asks for Clarification": "Clarify",
        "Check-ins with Teacher": "Check-in",
        "Asks for Ways to Improve": "Improve",
        "In-class Work Completed": "Complete"
    }
    
    # Create sticky header with full measure names
    st.markdown("""
    <style>
    .measure-header {
        position: sticky;
        top: 0;
        background-color: white;
        z-index: 999;
        padding: 10px 0;
        border-bottom: 2px solid #ddd;
        margin-bottom: 10px;
    }
    .measure-header table {
        width: 100%;
        font-weight: bold;
        font-size: 0.8em;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header row with full measure names
    header_cols = st.columns([2, 1, 1, 0.7] + [1] * len(utils.ENGAGEMENT_MEASURES))
    header_cols[0].markdown("**Student**")
    header_cols[1].markdown("**Last Obs**")
    header_cols[2].markdown("**Status**")
    header_cols[3].markdown("**Attend.**")
    
    for i, measure in enumerate(utils.ENGAGEMENT_MEASURES):
        header_cols[4 + i].markdown(f"**{measure_abbrev.get(measure, measure[:8])}**", 
                                     help=measure)
    
    st.markdown("---")
    
    # Create a form for better keyboard handling
    with st.form(key="observation_form", clear_on_submit=False):
        
        # Display students in table format with repeated headers
        for idx, (row_idx, student) in enumerate(class_students.iterrows()):
            student_id = student['student_id']
            
            # Repeat headers every 5 students
            if idx > 0 and idx % 5 == 0:
                st.markdown("---")
                header_cols = st.columns([2, 1, 1, 0.7] + [1] * len(utils.ENGAGEMENT_MEASURES))
                header_cols[0].markdown("**Student**")
                header_cols[1].markdown("**Last Obs**")
                header_cols[2].markdown("**Status**")
                header_cols[3].markdown("**Attend.**")
                
                for i, measure in enumerate(utils.ENGAGEMENT_MEASURES):
                    header_cols[4 + i].markdown(f"**{measure_abbrev.get(measure, measure[:8])}**",
                                                 help=measure)
                st.markdown("---")
            
            # Create columns for this student row
            cols = st.columns([2, 1, 1, 0.7] + [1] * len(utils.ENGAGEMENT_MEASURES))
            
            # Student name
            cols[0].markdown(f"**{student['name']}**")
            
            # Last observation
            days_since = student['last_obs_date']
            if days_since is None:
                cols[1].markdown("Never")
            else:
                cols[1].markdown(f"{days_since}d ago")
            
            # Status indicator
            emoji, label, color = utils.get_status_indicator(days_since)
            cols[2].markdown(f"{emoji} {label}")
            
            # P/A radio button (shortened labels)
            attendance_key = f"attendance_{student_id}_{observation_date}"
            
            # Get current attendance status
            current_attendance = st.session_state.attendance_status.get(attendance_key, "P")
            
            attendance = cols[3].radio(
                f"Attendance for {student['name']}",
                options=["P", "A"],
                index=0 if current_attendance == "P" else 1,
                key=attendance_key,
                label_visibility="collapsed",
                horizontal=False
            )
            
            # Update session state
            st.session_state.attendance_status[attendance_key] = attendance
            
            # Entry fields for each measure
            for i, measure in enumerate(utils.ENGAGEMENT_MEASURES):
                key = f"{student_id}_{measure}_{observation_date}"
                
                # Get current value from session state
                current_value = st.session_state.entry_grid.get(key, "")
                
                # If attendance is A (Absent), fill with "-"
                if attendance == "A":
                    value = "-"
                    st.session_state.entry_grid[key] = "-"
                    # Display as disabled field showing "-"
                    cols[4 + i].text_input(
                        f"obs_{key}",
                        value="-",
                        key=f"display_{key}",
                        label_visibility="collapsed",
                        disabled=True,
                        max_chars=1
                    )
                else:
                    # If changed from A to P, clear the value
                    if current_value == "-" and f"prev_attendance_{student_id}" in st.session_state:
                        if st.session_state[f"prev_attendance_{student_id}"] == "A":
                            current_value = ""
                            st.session_state.entry_grid[key] = ""
                    
                    # Text input for manual entry
                    value = cols[4 + i].text_input(
                        f"obs_{key}",
                        value=current_value,
                        key=key,
                        label_visibility="collapsed",
                        max_chars=1,
                        help="Type 1, 0, or -"
                    )
                    
                    # Validate and update session state
                    if value in ['1', '0', '-', '']:
                        st.session_state.entry_grid[key] = value
                    else:
                        # Invalid entry - reset
                        st.session_state.entry_grid[key] = ""
            
            # Store previous attendance for comparison
            st.session_state[f"prev_attendance_{student_id}"] = attendance
        
        # Submit button at bottom of form
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            save_button = st.form_submit_button("💾 Save Observations", type="primary", use_container_width=True)
        
        with col2:
            clear_button = st.form_submit_button("🗑️ Clear Grid", use_container_width=True)
        
        if save_button:
            save_observations(observation_date, selected_class, class_students)
        
        if clear_button:
            st.session_state.entry_grid = {}
            st.session_state.attendance_status = {}
            st.rerun()
    
    # Show count of entries
    filled_entries = sum(1 for v in st.session_state.entry_grid.values() if v in ['1', '0', '-'])
    total_possible = len(class_students) * len(utils.ENGAGEMENT_MEASURES)
    
    st.markdown(f"**Entries filled:** {filled_entries} / {total_possible}")
    
    # Add JavaScript for auto-tab functionality
    st.markdown("""
    <script>
    // Auto-tab after single character entry
    document.addEventListener('input', function(e) {
        if (e.target.tagName === 'INPUT' && e.target.type === 'text' && e.target.maxLength === 1) {
            if (e.target.value.length === 1) {
                // Find next input field
                const inputs = Array.from(document.querySelectorAll('input[type="text"]'));
                const currentIndex = inputs.indexOf(e.target);
                if (currentIndex >= 0 && currentIndex < inputs.length - 1) {
                    inputs[currentIndex + 1].focus();
                    inputs[currentIndex + 1].select();
                }
            }
        }
    });
    
    // Enter key moves down to same column
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.target.tagName === 'INPUT' && e.target.type === 'text') {
            e.preventDefault();
            const inputs = Array.from(document.querySelectorAll('input[type="text"]'));
            const currentIndex = inputs.indexOf(e.target);
            
            // Calculate column position (9 measures per row)
            const colPosition = currentIndex % 9;
            const nextRowIndex = currentIndex + 9;
            
            if (nextRowIndex < inputs.length) {
                inputs[nextRowIndex].focus();
                inputs[nextRowIndex].select();
            }
        }
    });
    </script>
    """, unsafe_allow_html=True)


def save_observations(observation_date, class_code, class_students):
    """Save observations to database with smart update/add logic"""
    
    observations_to_save = []
    entry_count = 0
    students_with_entries = set()
    
    for idx, student in class_students.iterrows():
        student_has_data = False
        for measure in utils.ENGAGEMENT_MEASURES:
            key = f"{student['student_id']}_{measure}_{observation_date}"
            value = st.session_state.entry_grid.get(key, "")
            
            # Only save if a value was entered
            if value in ['1', '0', '-']:
                observations_to_save.append({
                    'date': observation_date,
                    'class_code': class_code,
                    'student_id': student['student_id'],
                    'measure_name': measure,
                    'value': value
                })
                entry_count += 1
                student_has_data = True
        
        if student_has_data:
            students_with_entries.add(student['student_id'])
    
    if entry_count == 0:
        st.warning("⚠️ No observations to save. Please enter at least one observation.")
        return
    
    # Check if observations already exist for this date/class
    existing_obs = db.load_observations()
    existing_mask = (pd.to_datetime(existing_obs['date']).dt.date == observation_date) & \
                   (existing_obs['class_code'] == class_code)
    
    if existing_mask.any():
        # Check which students from entries already have data
        existing_student_ids = set(existing_obs[existing_mask]['student_id'].unique())
        students_to_overwrite = students_with_entries.intersection(existing_student_ids)
        students_to_add = students_with_entries - existing_student_ids
        
        # Count affected records
        existing_total = existing_mask.sum()
        total_students_in_existing = len(existing_student_ids)
        
        # Determine save mode
        if len(students_to_add) > 0 and len(students_to_overwrite) == 0:
            # ADDITIVE MODE - only adding new students, not touching existing
            st.info(f"""
            ### ➕ Adding New Student Data
            
            **Adding observations for:**
            - {len(students_to_add)} new student(s)
            - Date: {observation_date}
            - Class: {class_code}
            
            **Existing data for {total_students_in_existing} other students will be preserved.**
            """)
            
            # Save new observations without deleting anything
            db.add_observations(observations_to_save)
            
            st.success(f"✅ Added {entry_count} observations for {len(students_to_add)} new student(s)")
            
            # Clear the grid
            st.session_state.entry_grid = {}
            st.session_state.attendance_status = {}
            st.balloons()
            
        else:
            # UPDATE/OVERWRITE MODE - modifying existing students
            st.error(f"""
            ### ⚠️ UPDATE WARNING
            
            **This will update/overwrite data for:**
            - {len(students_to_overwrite)} student(s) you entered
            
            **Data for {total_students_in_existing - len(students_to_overwrite)} other students will be preserved.**
            
            **Students affected:** {', '.join(students_to_overwrite)}
            
            Are you sure you want to continue?
            """)
            
            # Create confirmation buttons
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button("✅ Yes, Update", type="primary", key="confirm_update"):
                    # Delete ONLY the students we're updating
                    for student_id in students_to_overwrite:
                        student_mask = existing_mask & (existing_obs['student_id'] == student_id)
                        # Remove these specific records
                        observations_to_keep = existing_obs[~student_mask]
                    
                    # Delete observations for ONLY the students we're updating
                    existing_obs_filtered = existing_obs[existing_mask]
                    students_to_delete_mask = existing_obs_filtered['student_id'].isin(students_to_overwrite)
                    
                    if students_to_delete_mask.any():
                        # This is a workaround - we need to delete by student
                        for student_id in students_to_overwrite:
                            # Delete observations for this specific student on this date/class
                            obs_to_remove = existing_obs[
                                (pd.to_datetime(existing_obs['date']).dt.date == observation_date) & 
                                (existing_obs['class_code'] == class_code) &
                                (existing_obs['student_id'] == student_id)
                            ]
                            # Note: This is a limitation - we'd need a delete_student_observations function
                            # For now, we'll do a full delete and re-add all
                    
                    # WORKAROUND: Delete all observations for this date/class, then re-add
                    # Keep observations we want to preserve
                    observations_to_keep = existing_obs[~existing_mask].to_dict('records')
                    observations_to_keep_for_date = existing_obs[
                        existing_mask & ~existing_obs['student_id'].isin(students_to_overwrite)
                    ].to_dict('records')
                    
                    # Delete all for this date/class
                    db.delete_observations(observation_date, class_code)
                    
                    # Re-add what we want to keep plus new data
                    all_observations = observations_to_keep_for_date + observations_to_save
                    db.add_observations(all_observations)
                    
                    st.success(f"✅ Updated {len(students_to_overwrite)} student(s). Other data preserved.")
                    
                    # Clear the grid
                    st.session_state.entry_grid = {}
                    st.session_state.attendance_status = {}
                    st.balloons()
            
            with col2:
                if st.button("❌ Cancel", key="cancel_update"):
                    st.info("Save cancelled. No changes made.")
                    return
            
            # Stop here - wait for user to click a button
            st.stop()
    
    else:
        # No existing data - save directly
        db.add_observations(observations_to_save)
        
        st.success(f"✅ Saved {entry_count} observations for {class_code} on {observation_date}")
        
        # Clear the grid
        st.session_state.entry_grid = {}
        st.session_state.attendance_status = {}
        st.balloons()
