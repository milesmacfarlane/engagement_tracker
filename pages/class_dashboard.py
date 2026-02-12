"""
Class Dashboard Page - Class-wide performance reports
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import database as db
import utils


def render():
    """Render the Class Dashboard page"""
    
    st.title("📚 Class Dashboard")
    st.markdown("View class-wide performance summary and analytics")
    
    # Load data
    students_df = db.load_students()
    classes_df = db.load_classes()
    observations_df = db.load_observations()
    
    # Check if data exists
    if len(classes_df) == 0:
        st.warning("⚠️ No classes found. Please add classes in the Setup page first.")
        return
    
    # Class selector
    selected_class = st.selectbox(
        "Select Class",
        options=classes_df['class_code'].tolist(),
        format_func=lambda x: f"{x} - {classes_df[classes_df['class_code']==x]['class_name'].values[0]}",
        help="Choose a class to view performance summary"
    )
    
    if not selected_class:
        return
    
    # Get class info
    class_info = classes_df[classes_df['class_code'] == selected_class].iloc[0]
    
    st.markdown("---")
    st.header(f"{class_info['class_name']}")
    
    # Get class summary
    summary = utils.get_class_performance_summary(observations_df, students_df, selected_class)
    
    if len(summary) == 0:
        st.warning(f"⚠️ No students found in class {selected_class}")
        return
    
    summary_df = pd.DataFrame(summary)
    
    # Calculate class statistics - check if students have any observation days
    students_with_data = summary_df[summary_df['Days Present'].apply(
        lambda x: int(x.split('/')[1]) if isinstance(x, str) and '/' in x else 0
    ) > 0]
    
    if len(students_with_data) == 0:
        st.info("ℹ️ No observations recorded for students in this class yet.")
        return
    
    # Class-level metrics
    st.markdown("### 📊 Class Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_students = len(summary_df)
        students_observed = len(students_with_data)
        st.metric(
            "Students Enrolled",
            total_students,
            help="Total number of students in this class"
        )
    
    with col2:
        st.metric(
            "Students Observed",
            students_observed,
            help="Number of students with at least one observation"
        )
    
    with col3:
        # Calculate class average achievement (only for students with valid observations)
        students_with_valid = students_with_data[students_with_data['Achievement %'].notna()]
        if len(students_with_valid) > 0:
            class_avg_achievement = students_with_valid['Achievement %'].mean()
            st.metric(
                "Class Avg Achievement",
                f"{class_avg_achievement:.1f}%",
                help="Average achievement % across all students with valid observations"
            )
        else:
            st.metric("Class Avg Achievement", "N/A")
    
    with col4:
        if len(students_with_data) > 0:
            # Count total observation days across all students
            total_obs_days = students_with_data['Days Present'].apply(
                lambda x: int(x.split('/')[1]) if isinstance(x, str) and '/' in x else 0
            ).sum()
            st.metric(
                "Total Observation Days",
                total_obs_days,
                help="Total observation days for this class"
            )
        else:
            st.metric("Total Observation Days", 0)
    
    st.markdown("---")
    
    # Performance band distribution
    st.markdown("### 📈 Performance Distribution")
    
    # Count students by performance band
    band_counts = {}
    for band_info in utils.PERFORMANCE_BANDS:
        band_name = band_info[2]
        band_counts[band_name] = 0
    
    band_counts["No Data"] = 0
    
    for _, student in summary_df.iterrows():
        perf = student['Achievement %']
        if pd.isna(perf):
            band_counts["No Data"] += 1
        else:
            band_name, _ = utils.get_performance_band(perf)
            band_counts[band_name] += 1
    
    # Display as columns
    cols = st.columns(len(band_counts))
    for i, (band, count) in enumerate(band_counts.items()):
        with cols[i]:
            st.metric(band, count)
    
    st.markdown("---")
    
    # Engagement Patterns Section (NEW)
    st.markdown("### 🎯 Class Engagement Patterns")
    st.caption("Understanding attendance-achievement relationships and intervention priorities")
    
    # Get engagement insights
    class_students = students_df[students_df['primary_class'] == selected_class]
    insights = utils.get_engagement_insights(observations_df, class_students)
    distribution = utils.get_class_engagement_distribution(observations_df, class_students)
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Avg Effective Engagement",
            f"{insights['avg_effective_engagement']:.1f}%",
            help="Average Effective Engagement Score (accounts for both attendance and achievement)"
        )
    
    with col2:
        correlation = insights['correlation']
        corr_interpretation = "Strong" if abs(correlation) > 0.7 else "Moderate" if abs(correlation) > 0.4 else "Weak"
        st.metric(
            "Attendance-Achievement Link",
            f"{corr_interpretation} ({correlation:.2f})",
            help="Correlation between attendance and achievement (-1 to 1)"
        )
    
    with col3:
        st.metric(
            "Present but Disengaged ⚠️",
            insights['present_but_disengaged_count'],
            help="Students attending regularly but not engaging (high attendance, low achievement)"
        )
    
    with col4:
        st.metric(
            "Engaged but Absent 📚",
            insights['engaged_but_absent_count'],
            help="Students engaged when present but poor attendance (low attendance, high achievement)"
        )
    
    # Engagement type distribution
    st.markdown("#### Student Type Distribution")
    
    dist_col1, dist_col2 = st.columns([2, 1])
    
    with dist_col1:
        # Create DataFrame for visualization
        dist_data = []
        for category, count in distribution.items():
            if count > 0:  # Only show categories with students
                dist_data.append({'Type': category, 'Count': count})
        
        if dist_data:
            dist_df = pd.DataFrame(dist_data)
            
            # Color mapping
            color_map = {
                'Exemplary': '#00B050',
                'Present but Disengaged': '#FF9900',
                'Engaged but Absent': '#FFC000',
                'Critical Intervention Needed': '#FF0000',
                'Developing - Focus Engagement': '#92D050',
                'Developing - Focus Attendance': '#FFFF00',
                'Unknown': '#D9D9D9'
            }
            
            fig = px.bar(
                dist_df,
                x='Type',
                y='Count',
                color='Type',
                color_discrete_map=color_map,
                title="Students by Engagement Type"
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No engagement data available yet")
    
    with dist_col2:
        st.markdown("**What This Means:**")
        st.markdown("""
        - **⭐ Exemplary:** Keep doing what works
        - **⚠️ Present but Disengaged:** Focus on engagement strategies
        - **📚 Engaged but Absent:** Address attendance barriers
        - **🚨 Critical:** Comprehensive intervention needed
        - **📈/📅 Developing:** Targeted support
        """)
    
    # Primary barriers breakdown
    st.markdown("#### Primary Barriers to Success")
    
    barrier_col1, barrier_col2 = st.columns([1, 2])
    
    with barrier_col1:
        barriers = insights['primary_barrier_counts']
        st.metric("Attendance Barriers", barriers.get('Attendance', 0))
        st.metric("Engagement Barriers", barriers.get('Engagement', 0))
        st.metric("Balanced (Both)", barriers.get('Balanced', 0))
    
    with barrier_col2:
        st.markdown("""
        **Intervention Priorities:**
        
        **If Attendance is primary barrier:**
        - Contact families about attendance patterns
        - Explore transportation/health/home barriers
        - Consider alternative schedules or supports
        
        **If Engagement is primary barrier:**
        - Review instructional strategies
        - Check for learning difficulties
        - Increase hands-on activities
        - Build relationships and relevance
        
        **If Balanced (both issues):**
        - Start with engagement (builds motivation)
        - Then address attendance
        - May need comprehensive support plan
        """)
    
    # Average opportunity lost
    if insights['opportunity_lost_avg'] > 10:
        st.warning(f"""
        ⚠️ **Significant Opportunity Lost:** On average, students in this class are losing 
        {insights['opportunity_lost_avg']:.1f}% of their potential engagement due to absence. 
        This suggests attendance interventions could have substantial impact.
        """)
    
    st.markdown("---")
    
    # Student performance table
    st.markdown("### 👥 Student Performance Table")
    
    # Add sort option
    sort_col = st.radio(
        "Sort by:",
        options=["Student Name", "Attendance % (Descending)", "Achievement % (Ascending)", "Achievement % (Descending)"],
        horizontal=True
    )
    
    # Sort the dataframe
    display_df = summary_df.copy()
    
    if sort_col == "Student Name":
        display_df = display_df.sort_values('Student Name')
    elif sort_col == "Attendance % (Descending)":
        display_df = display_df.sort_values('Attendance %', ascending=False, na_position='last')
    elif sort_col == "Achievement % (Ascending)":
        display_df = display_df.sort_values('Achievement %', na_position='last')
    elif sort_col == "Achievement % (Descending)":
        display_df = display_df.sort_values('Achievement %', ascending=False, na_position='last')
    
    # Format percentages for display
    display_df['Attendance %'] = display_df['Attendance %'].apply(utils.format_percentage)
    display_df['Achievement %'] = display_df['Achievement %'].apply(utils.format_percentage)
    
    # Select columns to display
    display_columns = [
        'Student Name',
        'Attendance %',
        'Days Present',
        'Days Absent',
        'Achievement %',
        'Band',
        'Status',
        'Days Since Last'
    ]
    
    # Display table
    st.dataframe(
        display_df[display_columns],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Attendance %": st.column_config.TextColumn("Attendance %", width="small"),
            "Achievement %": st.column_config.TextColumn("Achievement %", width="small"),
            "Band": st.column_config.TextColumn("Band", width="medium"),
            "Status": st.column_config.TextColumn("Status", width="medium")
        }
    )
    
    # Download button
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name=f"{selected_class}_performance_summary.csv",
        mime="text/csv"
    )
    
    st.markdown("---")
    
    # Visualizations
    st.markdown("### 📊 Class Analytics")
    
    # Performance distribution chart
    students_with_valid = students_with_data[students_with_data['Achievement %'].notna()].copy()
    
    if len(students_with_valid) > 0:
        # Convert formatted percentage back to numeric for charting
        students_with_valid['Achievement_Numeric'] = students_with_valid.apply(
            lambda row: row['Achievement %'] if isinstance(row['Achievement %'], (int, float)) 
            else summary_df[summary_df['Student Name'] == row['Student Name']]['Achievement %'].values[0],
            axis=1
        )
        
        # Histogram of performance
        fig = px.histogram(
            students_with_valid,
            x='Achievement_Numeric',
            nbins=20,
            title="Distribution of Student Achievement",
            labels={'Achievement_Numeric': 'Achievement %'},
            color_discrete_sequence=[utils.COLORS['primary']]
        )
        
        fig.update_layout(
            xaxis_title="Achievement %",
            yaxis_title="Number of Students",
            showlegend=False,
            xaxis=dict(range=[0, 100])
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Top and bottom performers
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🌟 Top Performers (Top 5)")
            top_5 = summary_df[summary_df['Achievement %'].notna()].nlargest(5, 'Achievement %')
            
            for idx, student in top_5.iterrows():
                st.markdown(f"**{student['Student Name']}** - {utils.format_percentage(student['Achievement %'])}")
        
        with col2:
            st.markdown("#### ⚠️ Students Needing Support (Bottom 5)")
            bottom_5 = summary_df[summary_df['Achievement %'].notna()].nsmallest(5, 'Achievement %')
            
            for idx, student in bottom_5.iterrows():
                st.markdown(f"**{student['Student Name']}** - {utils.format_percentage(student['Achievement %'])}")
    
    # Students requiring observation
    st.markdown("---")
    st.markdown("### 🔍 Observation Priority")
    
    # Students with no observations (check by Days Present column)
    no_obs = summary_df[summary_df['Days Present'].apply(
        lambda x: int(x.split('/')[1]) if isinstance(x, str) and '/' in x else 0
    ) == 0]
    
    if len(no_obs) > 0:
        st.warning(f"⚠️ **{len(no_obs)} students** have no observations recorded")
        with st.expander("View students with no observations"):
            st.dataframe(
                no_obs[['Student Name', 'Student ID']],
                hide_index=True,
                use_container_width=True
            )
    
    # Students overdue for observation
    overdue = summary_df[summary_df['Days Since Last'].apply(
        lambda x: isinstance(x, int) and x > 7
    )]
    
    if len(overdue) > 0:
        st.warning(f"🔴 **{len(overdue)} students** overdue for observation (>7 days)")
        with st.expander("View overdue students"):
            st.dataframe(
                overdue[['Student Name', 'Days Since Last', 'Achievement %']],
                hide_index=True,
                use_container_width=True
            )
    
    # Advanced analytics (optional)
    if st.checkbox("Show Advanced Analytics", value=False):
        st.markdown("---")
        st.markdown("### 🔬 Advanced Analytics")
        
        # Measure difficulty analysis
        st.markdown("#### Measure Performance Across Class")
        
        measure_stats = []
        for measure in utils.ENGAGEMENT_MEASURES:
            measure_obs = observations_df[
                (observations_df['class_code'] == selected_class) &
                (observations_df['measure_name'] == measure)
            ]
            
            if len(measure_obs) > 0:
                perf, ones, zeros, absent, valid = utils.calculate_performance(measure_obs)
                measure_stats.append({
                    'Measure': measure,
                    'Achievement %': perf,
                    'Total Observations': len(measure_obs),
                    'Observed (1s)': ones,
                    'Not Observed (0s)': zeros,
                    'Valid': valid
                })
        
        if measure_stats:
            measure_df = pd.DataFrame(measure_stats)
            measure_df = measure_df.sort_values('Achievement %', ascending=False)
            
            # Create bar chart
            fig = go.Figure(data=[
                go.Bar(
                    x=measure_df['Measure'],
                    y=measure_df['Achievement %'],
                    marker_color=utils.COLORS['primary'],
                    text=measure_df['Achievement %'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A"),
                    textposition='outside'
                )
            ])
            
            fig.update_layout(
                title="Class Achievement by Engagement Measure",
                xaxis_title="Measure",
                yaxis_title="Achievement %",
                height=400,
                showlegend=False,
                yaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show table
            measure_df['Achievement %'] = measure_df['Achievement %'].apply(utils.format_percentage)
            st.dataframe(measure_df, hide_index=True, use_container_width=True)
