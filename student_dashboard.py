"""
Student Dashboard Page - Individual student performance reports
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import database as db
import utils


def render():
    """Render the Student Dashboard page"""
    
    st.title("👤 Student Dashboard")
    st.markdown("View detailed performance reports for individual students")
    
    # Load data
    students_df = db.load_students()
    classes_df = db.load_classes()
    observations_df = db.load_observations()
    
    # Check if data exists
    if len(students_df) == 0:
        st.warning("⚠️ No students found. Please add students in the Setup page first.")
        return
    
    # Selection controls
    col1, col2 = st.columns(2)
    
    with col1:
        # Optional class filter
        class_options = ['All Classes'] + classes_df['class_code'].tolist()
        selected_class_filter = st.selectbox(
            "Filter by Class (optional)",
            options=class_options,
            help="Optionally filter students by class"
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
            help="Choose a student to view their performance"
        )
    
    if not selected_student_id:
        return
    
    # Get student info
    student = students_df[students_df['student_id'] == selected_student_id].iloc[0]
    
    st.markdown("---")
    
    # Display student header
    st.header(f"{student['name']}")
    st.markdown(f"**Student ID:** {student['student_id']} | **Primary Class:** {student['primary_class']}")
    
    # Get student observations
    student_obs = observations_df[observations_df['student_id'] == selected_student_id]
    
    if len(student_obs) == 0:
        st.info("ℹ️ No observations recorded for this student yet.")
        return
    
    # Calculate overall performance
    overall_perf, ones, zeros, absent, valid = utils.calculate_performance(
        observations_df, student_id=selected_student_id
    )
    
    # Calculate attendance
    attendance_rate = utils.calculate_attendance_rate(observations_df, selected_student_id)
    total_days = utils.get_total_observation_days(observations_df, selected_student_id)
    days_absent = utils.get_days_absent(observations_df, selected_student_id)
    days_present = total_days - days_absent
    
    # Section 1: Performance Summary
    st.markdown("### 📊 Performance Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Attendance Rate",
            utils.format_percentage(attendance_rate),
            delta=None,
            help="Percentage of days student was present"
        )
    
    with col2:
        st.metric(
            "Achievement %",
            utils.format_percentage(overall_perf),
            delta=None,
            help="Percentage of observed behaviors (1s) out of valid observations"
        )
    
    with col3:
        band_name, band_color = utils.get_performance_band(overall_perf)
        st.metric(
            "Performance Band",
            band_name,
            help="Performance classification based on achievement percentage"
        )
    
    with col4:
        days_since = utils.get_days_since_last_observation(observations_df, selected_student_id)
        st.metric(
            "Days Since Last",
            days_since if days_since is not None else "N/A",
            help="Days since last observation"
        )
    
    # Additional metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Days Present", f"{days_present}/{total_days}")
    
    with col2:
        st.metric("Days Absent", days_absent)
    
    with col3:
        st.metric("Behaviors Observed (1s)", ones)
    
    with col4:
        st.metric("Not Observed (0s)", zeros)
    
    # Observation period
    first_date = pd.to_datetime(student_obs['date']).min().strftime('%Y-%m-%d')
    last_date = pd.to_datetime(student_obs['date']).max().strftime('%Y-%m-%d')
    st.markdown(f"**Observation Period:** {first_date} to {last_date}")
    
    st.markdown("---")
    
    # Section 1.5: Engagement Analysis (NEW)
    st.markdown("### 🎯 Engagement Analysis")
    st.caption("Understanding the relationship between attendance and achievement")
    
    # Calculate new engagement metrics
    achievement_pct, _, _, _, _ = utils.calculate_performance(observations_df, student_id=selected_student_id)
    effective_engagement = utils.calculate_effective_engagement(attendance_rate, achievement_pct)
    primary_barrier = utils.identify_primary_barrier(attendance_rate, achievement_pct)
    category, emoji, description, intervention = utils.classify_engagement_type(attendance_rate, achievement_pct)
    opportunity_lost = utils.calculate_opportunity_lost(attendance_rate, achievement_pct)
    
    # Display engagement metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Effective Engagement Score",
            f"{effective_engagement:.1f}%",
            delta=None,
            help="Combined score accounting for both attendance and achievement (Attendance × Achievement / 100)"
        )
    
    with col2:
        # Color code primary barrier
        if primary_barrier == "Engagement":
            barrier_color = "🟡"
        elif primary_barrier == "Attendance":
            barrier_color = "🔴"
        else:
            barrier_color = "🟢"
        
        st.metric(
            "Primary Barrier",
            f"{barrier_color} {primary_barrier}",
            delta=None,
            help="Whether attendance or engagement is the main barrier to success"
        )
    
    with col3:
        st.metric(
            "Opportunity Lost",
            f"{opportunity_lost:.1f}%",
            delta=None,
            help="Percentage of potential engagement lost due to absence"
        )
    
    # Student type classification
    st.markdown(f"""
    <div style='padding: 1rem; background-color: #f0f2f6; border-radius: 0.5rem; border-left: 4px solid #1f4788;'>
        <h4>{emoji} Student Type: {category}</h4>
        <p><strong>Pattern:</strong> {description}</p>
        <p><strong>Recommended Intervention:</strong> {intervention}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Section 2: Measure-by-Measure Breakdown
    st.markdown("### 📋 Measure-by-Measure Breakdown")
    
    breakdown = utils.get_student_measure_breakdown(observations_df, selected_student_id)
    breakdown_df = pd.DataFrame(breakdown)
    
    # Format percentage column
    breakdown_df['Performance %'] = breakdown_df['Performance %'].apply(utils.format_percentage)
    
    # Display table
    st.dataframe(
        breakdown_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Calculate measure performance dict for insights
    measure_performance = {}
    for item in breakdown:
        if item['Performance %'] != 'N/A':
            # Extract numeric value
            perf_val = None
            for b_item in breakdown:
                if b_item['Measure'] == item['Measure']:
                    perf, _, _, _, _ = utils.calculate_performance(
                        observations_df, student_id=selected_student_id, measure=item['Measure']
                    )
                    perf_val = perf
                    break
            measure_performance[item['Measure']] = perf_val
    
    st.markdown("---")
    
    # Section 3: Auto-Generated Achievements (Top 3 Strengths)
    st.markdown("### 🌟 Top Strengths")
    
    top_measures = utils.get_top_measures(measure_performance, n=3)
    
    if top_measures:
        for i, (measure, perf) in enumerate(top_measures, 1):
            st.markdown(f"**{i}. {measure}** - {perf:.1f}% (Consistently demonstrated)")
    else:
        st.info("No data available yet to identify strengths.")
    
    st.markdown("---")
    
    # Section 4: Auto-Generated Improvements Needed
    st.markdown("### 🎯 Focus Areas")
    
    improvement_areas = utils.get_improvement_areas(measure_performance, threshold=75, n=3)
    
    if improvement_areas:
        for i, (measure, perf) in enumerate(improvement_areas, 1):
            st.markdown(f"**{i}. {measure}** - {perf:.1f}% (Needs attention)")
    else:
        st.success("✅ All measures performing well (above 75%)")
    
    st.markdown("---")
    
    # Section 5: Recommended Next Steps
    st.markdown("### 💡 Recommended Next Steps")
    
    recommendations = utils.get_recommended_next_steps(overall_perf)
    st.info(recommendations)
    
    st.markdown("---")
    
    # Section 6: Performance Visualization
    st.markdown("### 📈 Visual Breakdown")
    
    # Create bar chart of measure performance
    if measure_performance:
        chart_data = pd.DataFrame([
            {'Measure': measure, 'Performance %': perf}
            for measure, perf in measure_performance.items()
            if perf is not None
        ])
        
        if len(chart_data) > 0:
            # Sort by performance
            chart_data = chart_data.sort_values('Performance %', ascending=True)
            
            # Create color mapping based on performance
            colors = []
            for perf in chart_data['Performance %']:
                if perf >= 85:
                    colors.append(utils.COLORS['success'])
                elif perf >= 75:
                    colors.append('#92D050')
                elif perf >= 65:
                    colors.append('#FFFF00')
                elif perf >= 50:
                    colors.append('#FFC000')
                else:
                    colors.append(utils.COLORS['error'])
            
            fig = go.Figure(data=[
                go.Bar(
                    y=chart_data['Measure'],
                    x=chart_data['Performance %'],
                    orientation='h',
                    marker_color=colors,
                    text=chart_data['Performance %'].apply(lambda x: f"{x:.1f}%"),
                    textposition='outside'
                )
            ])
            
            fig.update_layout(
                title="Performance by Engagement Measure",
                xaxis_title="Performance %",
                yaxis_title="",
                height=400,
                showlegend=False,
                xaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Optional: Recent Observation Timeline
    if st.checkbox("Show Recent Observation Timeline", value=False):
        st.markdown("### 📅 Recent Observations")
        
        # Get observation sessions (unique dates)
        obs_dates = pd.to_datetime(student_obs['date']).unique()
        obs_dates = sorted(obs_dates, reverse=True)[:10]
        
        timeline_data = []
        for obs_date in obs_dates:
            date_obs = student_obs[pd.to_datetime(student_obs['date']) == obs_date]
            perf, _, _, _, _ = utils.calculate_performance(date_obs)
            
            timeline_data.append({
                'Date': pd.to_datetime(obs_date).strftime('%Y-%m-%d'),
                'Performance %': perf
            })
        
        if timeline_data:
            timeline_df = pd.DataFrame(timeline_data)
            
            st.dataframe(
                timeline_df,
                use_container_width=True,
                hide_index=True
            )
