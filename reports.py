"""
Reports Page - Generate PDF reports for students and classes
"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta
import database as db
import pdf_reports


def render():
    """Render the Reports page"""
    
    st.title("📄 Generate Reports")
    st.markdown("Create professional PDF reports for students and classes")
    
    # Load data
    students_df = db.load_students()
    classes_df = db.load_classes()
    observations_df = db.load_observations()
    
    # Check if data exists
    if len(students_df) == 0 or len(classes_df) == 0:
        st.warning("⚠️ Please add students and classes in the Setup page first.")
        return
    
    if len(observations_df) == 0:
        st.info("ℹ️ No observations recorded yet. Reports will be empty.")
    
    # Tabs for different report types
    tab1, tab2 = st.tabs(["👤 Student Report", "📚 Class Report"])
    
    with tab1:
        render_student_report_generator(students_df, classes_df)
    
    with tab2:
        render_class_report_generator(classes_df)


def render_student_report_generator(students_df, classes_df):
    """Render student report generator"""
    
    st.subheader("Generate Student Engagement Report")
    st.markdown("Create a one-page PDF report for an individual student")
    
    # Student selection
    col1, col2 = st.columns(2)
    
    with col1:
        # Optional class filter
        class_options = ['All Classes'] + classes_df['class_code'].tolist()
        selected_class_filter = st.selectbox(
            "Filter by Class (optional)",
            options=class_options,
            help="Optionally filter students by class",
            key="student_report_class_filter"
        )
    
    # Filter students by class if selected
    if selected_class_filter != 'All Classes':
        filtered_students = students_df[students_df['primary_class'] == selected_class_filter]
    else:
        filtered_students = students_df
    
    with col2:
        # Student selector
        selected_student_id = st.selectbox(
            "Select Student",
            options=filtered_students['student_id'].tolist(),
            format_func=lambda x: f"{filtered_students[filtered_students['student_id']==x]['name'].values[0]} ({x})",
            help="Choose a student to generate report for",
            key="student_report_student"
        )
    
    # Date range selection
    st.markdown("### Report Period")
    
    date_range = st.radio(
        "Select date range for report",
        options=['ALL', 'MOST_RECENT', 'DATE_RANGE'],
        format_func=lambda x: {
            'ALL': 'All Observations',
            'MOST_RECENT': 'Most Recent (Last 30 Days)',
            'DATE_RANGE': 'Custom Date Range'
        }[x],
        horizontal=True,
        key="student_report_date_range"
    )
    
    start_date = None
    end_date = None
    
    if date_range == 'DATE_RANGE':
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=date.today() - timedelta(days=30),
                key="student_report_start_date"
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=date.today(),
                key="student_report_end_date"
            )
    
    st.markdown("---")
    
    # Generate button
    if st.button("📄 Generate Student Report", type="primary", use_container_width=True):
        with st.spinner("Generating PDF report..."):
            try:
                # Generate PDF
                pdf_buffer = pdf_reports.generate_student_report_pdf(
                    selected_student_id,
                    date_range=date_range,
                    start_date=start_date,
                    end_date=end_date
                )
                
                # Get student name for filename
                student_name = filtered_students[filtered_students['student_id']==selected_student_id]['name'].values[0]
                filename = f"student_report_{student_name.replace(' ', '_')}_{date.today()}.pdf"
                
                # Download button
                st.success("✅ Report generated successfully!")
                st.download_button(
                    label="📥 Download Student Report",
                    data=pdf_buffer,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"❌ Error generating report: {str(e)}")


def render_class_report_generator(classes_df):
    """Render class report generator"""
    
    st.subheader("Generate Class Engagement Report")
    st.markdown("Create a one-page PDF report for one or more classes")
    
    # Class selection
    st.markdown("### Select Classes")
    
    # Multiselect for classes
    selected_classes = st.multiselect(
        "Choose one or more classes",
        options=classes_df['class_code'].tolist(),
        format_func=lambda x: f"{x} - {classes_df[classes_df['class_code']==x]['class_name'].values[0]}",
        help="Select classes to include in the report",
        key="class_report_classes"
    )
    
    if not selected_classes:
        st.info("ℹ️ Please select at least one class to generate a report")
        return
    
    # Show selected classes
    if len(selected_classes) == 1:
        st.info(f"📚 Report will cover: **{selected_classes[0]}**")
    else:
        st.info(f"📚 Report will cover **{len(selected_classes)} classes**: {', '.join(selected_classes)}")
    
    # Date range selection
    st.markdown("### Report Period")
    
    date_range = st.radio(
        "Select date range for report",
        options=['ALL', 'MOST_RECENT', 'DATE_RANGE'],
        format_func=lambda x: {
            'ALL': 'All Observations',
            'MOST_RECENT': 'Most Recent (Last 30 Days)',
            'DATE_RANGE': 'Custom Date Range'
        }[x],
        horizontal=True,
        key="class_report_date_range"
    )
    
    start_date = None
    end_date = None
    
    if date_range == 'DATE_RANGE':
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=date.today() - timedelta(days=30),
                key="class_report_start_date"
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=date.today(),
                key="class_report_end_date"
            )
    
    st.markdown("---")
    
    # Generate button
    if st.button("📄 Generate Class Report", type="primary", use_container_width=True):
        with st.spinner("Generating PDF report..."):
            try:
                # Generate PDF
                pdf_buffer = pdf_reports.generate_class_report_pdf(
                    selected_classes,
                    date_range=date_range,
                    start_date=start_date,
                    end_date=end_date
                )
                
                # Create filename
                if len(selected_classes) == 1:
                    filename = f"class_report_{selected_classes[0]}_{date.today()}.pdf"
                else:
                    filename = f"class_report_multiple_classes_{date.today()}.pdf"
                
                # Download button
                st.success("✅ Report generated successfully!")
                st.download_button(
                    label="📥 Download Class Report",
                    data=pdf_buffer,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"❌ Error generating report: {str(e)}")
    
    # Report preview info
    st.markdown("---")
    st.markdown("### 📋 What's Included in Class Report")
    st.markdown("""
    - **Overall Class Statistics**: Total students, class average, observation count
    - **Students by Performance Band**: Students grouped by performance level
    - **Engagement Measures Analysis**: Average performance per measure with students needing attention
    - **Professional greyscale formatting** suitable for printing
    """)
