"""
Utility functions for engagement tracking calculations
"""
import pandas as pd
from datetime import datetime, timedelta

# 9 Engagement Measures
ENGAGEMENT_MEASURES = [
    "Time on Task",
    "Asked/Answered/Shared",
    "Work Completed/Ready",
    "Materials/Organized",
    "Helping/Asking for Help",
    "Asks for Clarification",
    "Check-ins with Teacher",
    "Asks for Ways to Improve",
    "In-class Work Completed"
]

# Performance Band Criteria
PERFORMANCE_BANDS = [
    (85, 100, "Exemplary", "#00B050"),
    (75, 85, "Proficient", "#92D050"),
    (65, 75, "Developing", "#FFFF00"),
    (50, 65, "Emerging", "#FFC000"),
    (40, 50, "Beginning", "#FF9900"),
    (0, 40, "Needs Intensive Support", "#FF0000")
]

# Color scheme
COLORS = {
    'primary': '#1F4788',
    'success': '#00B050',
    'warning': '#FF9900',
    'error': '#FFC7CE',
    'neutral': '#D9D9D9',
    'observed': '#00B050',
    'not_observed': '#FFC7CE',
    'absent': '#D9D9D9'
}


def calculate_performance(observations_df, student_id=None, measure=None):
    """
    Calculate performance % for observations
    
    Args:
        observations_df: DataFrame with observations
        student_id: Optional filter by student
        measure: Optional filter by measure
    
    Returns:
        tuple: (percentage, ones_count, zeros_count, absent_count, valid_count)
    """
    df = observations_df.copy()
    
    if student_id is not None:
        df = df[df['student_id'] == student_id]
    
    if measure is not None:
        df = df[df['measure_name'] == measure]
    
    if len(df) == 0:
        return None, 0, 0, 0, 0
    
    ones = len(df[df['value'] == '1'])
    zeros = len(df[df['value'] == '0'])
    absent = len(df[df['value'] == '-'])
    valid = ones + zeros
    
    if valid == 0:
        percentage = None
    else:
        percentage = (ones / valid) * 100
    
    return percentage, ones, zeros, absent, valid


def get_performance_band(percentage):
    """
    Map percentage to performance band
    
    Args:
        percentage: Performance percentage (0-100)
    
    Returns:
        tuple: (band_name, color)
    """
    if percentage is None:
        return "No Data", COLORS['neutral']
    
    for low, high, name, color in PERFORMANCE_BANDS:
        if low <= percentage < high or (high == 100 and percentage == 100):
            return name, color
    
    return "Unknown", COLORS['neutral']


def get_band_emoji(percentage):
    """Get emoji for performance band"""
    if percentage is None:
        return "⚠️"
    elif percentage >= 85:
        return "✓"
    elif percentage >= 65:
        return "→"
    else:
        return "⚠️"


def get_top_measures(measure_performance_dict, n=3):
    """
    Return top N measures by performance %
    
    Args:
        measure_performance_dict: Dict of {measure_name: percentage}
        n: Number of top measures to return
    
    Returns:
        list: [(measure_name, percentage), ...]
    """
    # Filter out None values
    valid_measures = {k: v for k, v in measure_performance_dict.items() if v is not None}
    
    if not valid_measures:
        return []
    
    # Sort by percentage descending
    sorted_measures = sorted(valid_measures.items(), key=lambda x: x[1], reverse=True)
    
    return sorted_measures[:n]


def get_improvement_areas(measure_performance_dict, threshold=75, n=3):
    """
    Return measures below threshold, sorted ascending
    
    Args:
        measure_performance_dict: Dict of {measure_name: percentage}
        threshold: Threshold percentage (default 75)
        n: Max number of measures to return
    
    Returns:
        list: [(measure_name, percentage), ...]
    """
    # Filter measures below threshold
    below_threshold = {k: v for k, v in measure_performance_dict.items() 
                      if v is not None and v < threshold}
    
    if not below_threshold:
        return []
    
    # Sort by percentage ascending
    sorted_measures = sorted(below_threshold.items(), key=lambda x: x[1])
    
    return sorted_measures[:n]


def get_recommended_next_steps(percentage):
    """
    Generate recommended next steps based on overall performance
    
    Args:
        percentage: Overall performance percentage
    
    Returns:
        str: Recommended actions
    """
    if percentage is None:
        return "No observations recorded yet. Begin regular observations to track progress."
    
    if percentage >= 85:
        return ("Continue current strategies. Consider leadership opportunities for this student. "
                "Monitor sustained performance and celebrate successes.")
    elif percentage >= 65:
        return ("Provide targeted support in focus areas. Schedule regular check-ins to monitor progress. "
                "Celebrate strengths while addressing areas for growth.")
    else:
        return ("Immediate intervention recommended. Daily check-ins required. "
                "Develop individualized support plan. Parent communication advised.")


def get_status_indicator(days_since_last):
    """
    Get status indicator based on days since last observation
    
    Args:
        days_since_last: Number of days since last observation
    
    Returns:
        tuple: (emoji, label, color)
    """
    if days_since_last is None:
        return "⚠️", "No Data", COLORS['warning']
    elif days_since_last <= 3:
        return "✓", "Recent", COLORS['success']
    elif days_since_last <= 7:
        return "⚠️", "Follow Up", COLORS['warning']
    else:
        return "🔴", "Overdue", COLORS['error']


def get_days_since_last_observation(observations_df, student_id):
    """
    Calculate days since last observation for a student
    
    Args:
        observations_df: DataFrame with observations
        student_id: Student ID
    
    Returns:
        int or None: Days since last observation
    """
    student_obs = observations_df[observations_df['student_id'] == student_id]
    
    if len(student_obs) == 0:
        return None
    
    last_date = pd.to_datetime(student_obs['date']).max()
    today = datetime.now().date()
    days = (today - last_date.date()).days
    
    return days


def format_percentage(percentage):
    """Format percentage for display"""
    if percentage is None:
        return "N/A"
    return f"{percentage:.1f}%"


def validate_observation_value(value):
    """
    Validate observation value
    
    Args:
        value: Input value
    
    Returns:
        bool: True if valid ('1', '0', or '-')
    """
    return value in ['1', '0', '-']


def get_student_measure_breakdown(observations_df, student_id):
    """
    Get measure-by-measure breakdown for a student
    
    Args:
        observations_df: DataFrame with observations
        student_id: Student ID
    
    Returns:
        list: List of dicts with measure statistics
    """
    breakdown = []
    
    for measure in ENGAGEMENT_MEASURES:
        perf, ones, zeros, absent, valid = calculate_performance(
            observations_df, student_id=student_id, measure=measure
        )
        
        # Total observations for this measure (not used for absence count)
        total = ones + zeros + absent
        
        breakdown.append({
            'Measure': measure,
            'Total': total,
            '1s (Observed)': ones,
            '0s (Not Observed)': zeros,
            '- (Absent)': absent,
            'Valid Observations': valid,
            'Performance %': perf,
            'Band': get_performance_band(perf)[0],
            'Status': get_band_emoji(perf)
        })
    
    return breakdown


def get_days_absent(observations_df, student_id):
    """
    Calculate number of days student was absent
    
    Args:
        observations_df: DataFrame with observations
        student_id: Student ID
    
    Returns:
        int: Number of unique dates where student was absent
    """
    student_obs = observations_df[observations_df['student_id'] == student_id]
    
    if len(student_obs) == 0:
        return 0
    
    # Get unique dates where ANY observation was marked as absent
    absent_dates = student_obs[student_obs['value'] == '-']['date'].unique()
    
    return len(absent_dates)


def get_total_observation_days(observations_df, student_id):
    """
    Calculate total number of days student was observed (present or absent)
    
    Args:
        observations_df: DataFrame with observations
        student_id: Student ID
    
    Returns:
        int: Number of unique observation dates
    """
    student_obs = observations_df[observations_df['student_id'] == student_id]
    
    if len(student_obs) == 0:
        return 0
    
    return len(student_obs['date'].unique())


def calculate_attendance_rate(observations_df, student_id):
    """
    Calculate attendance rate for a student
    
    Args:
        observations_df: DataFrame with observations
        student_id: Student ID
    
    Returns:
        float or None: Attendance percentage (0-100), or None if no observations
    """
    total_days = get_total_observation_days(observations_df, student_id)
    
    if total_days == 0:
        return None
    
    absent_days = get_days_absent(observations_df, student_id)
    present_days = total_days - absent_days
    
    return (present_days / total_days) * 100


def get_class_performance_summary(observations_df, students_df, class_code):
    """
    Get performance summary for all students in a class
    
    Args:
        observations_df: DataFrame with observations
        students_df: DataFrame with student roster
        class_code: Class code to filter
    
    Returns:
        list: List of dicts with student statistics
    """
    class_students = students_df[students_df['primary_class'] == class_code]
    summary = []
    
    for _, student in class_students.iterrows():
        perf, ones, zeros, absent, valid = calculate_performance(
            observations_df, student_id=student['student_id']
        )
        
        # Calculate attendance
        attendance_rate = calculate_attendance_rate(observations_df, student['student_id'])
        total_days = get_total_observation_days(observations_df, student['student_id'])
        days_absent = get_days_absent(observations_df, student['student_id'])
        days_present = total_days - days_absent
        
        days_since = get_days_since_last_observation(observations_df, student['student_id'])
        status_emoji, status_label, _ = get_status_indicator(days_since)
        
        # Determine status
        if total_days == 0:
            status = "⚠️ No Data"
        elif perf is not None:
            if perf < 50:
                status = "🔴 Below 50%"
            elif perf < 75:
                status = "⚠️ Watch"
            else:
                status = "✓ Good"
        else:
            status = "⚠️ No Valid Data"
        
        summary.append({
            'Student Name': student['name'],
            'Student ID': student['student_id'],
            'Attendance %': attendance_rate,
            'Days Present': f"{days_present}/{total_days}",
            'Days Absent': days_absent,
            'Achievement %': perf,
            'Behaviors Observed (1s)': ones,
            'Not Observed (0s)': zeros,
            'Valid Observations': valid,
            'Band': get_performance_band(perf)[0],
            'Status': status,
            'Days Since Last': days_since if days_since is not None else "Never"
        })
    
    return summary


def create_sample_data():
    """
    Create sample data for demonstration
    
    Returns:
        tuple: (students_df, classes_df, observations_df)
    """
    import random
    from datetime import date, timedelta
    
    # Classes
    classes = [
        {'class_code': 'HIS20A', 'class_name': 'History 20 - Section A'},
        {'class_code': 'HIS20B', 'class_name': 'History 20 - Section B'},
        {'class_code': 'SST20', 'class_name': 'Social Studies 20'}
    ]
    classes_df = pd.DataFrame(classes)
    
    # Students (20-25 per class)
    students = []
    student_id = 100001
    
    first_names = ['Emma', 'Liam', 'Olivia', 'Noah', 'Ava', 'Ethan', 'Sophia', 'Mason',
                   'Isabella', 'William', 'Mia', 'James', 'Charlotte', 'Benjamin', 'Amelia',
                   'Lucas', 'Harper', 'Henry', 'Evelyn', 'Alexander', 'Abigail', 'Michael',
                   'Emily', 'Daniel', 'Elizabeth', 'Matthew', 'Sofia', 'Jackson', 'Avery',
                   'Sebastian', 'Ella', 'David', 'Scarlett', 'Joseph', 'Grace', 'Carter',
                   'Chloe', 'Owen', 'Victoria', 'Wyatt', 'Riley', 'John', 'Aria', 'Jack',
                   'Lily', 'Luke', 'Aubrey', 'Jayden', 'Zoey', 'Dylan', 'Penelope', 'Grayson',
                   'Lillian', 'Levi', 'Addison', 'Isaac', 'Layla', 'Gabriel', 'Natalie',
                   'Julian', 'Camila', 'Mateo', 'Hannah', 'Anthony', 'Brooklyn', 'Jaxon']
    
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
                  'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
                  'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
                  'Lee', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez']
    
    for class_code in ['HIS20A', 'HIS20B', 'SST20']:
        num_students = random.randint(20, 25)
        for i in range(num_students):
            students.append({
                'student_id': str(student_id),
                'name': f"{random.choice(first_names)} {random.choice(last_names)}",
                'primary_class': class_code
            })
            student_id += 1
    
    students_df = pd.DataFrame(students)
    
    # Observations (10 school days, realistic patterns)
    observations = []
    start_date = date.today() - timedelta(days=14)
    observation_dates = [start_date + timedelta(days=i) for i in range(0, 14, 1)
                        if (start_date + timedelta(days=i)).weekday() < 5][:10]
    
    for obs_date in observation_dates:
        # Each class gets observed roughly every 2-3 days
        if random.random() < 0.4:
            class_to_observe = random.choice(['HIS20A', 'HIS20B', 'SST20'])
            class_students = students_df[students_df['primary_class'] == class_to_observe]
            
            for _, student in class_students.iterrows():
                # Some students have better engagement patterns
                student_performance_level = random.choices(
                    ['high', 'medium', 'low', 'absent'],
                    weights=[0.3, 0.4, 0.2, 0.1]
                )[0]
                
                if student_performance_level == 'absent':
                    # Student was absent
                    for measure in ENGAGEMENT_MEASURES:
                        observations.append({
                            'date': obs_date,
                            'class_code': class_to_observe,
                            'student_id': student['student_id'],
                            'measure_name': measure,
                            'value': '-'
                        })
                else:
                    # Student was present
                    for measure in ENGAGEMENT_MEASURES:
                        if student_performance_level == 'high':
                            value = random.choices(['1', '0'], weights=[0.85, 0.15])[0]
                        elif student_performance_level == 'medium':
                            value = random.choices(['1', '0'], weights=[0.70, 0.30])[0]
                        else:  # low
                            value = random.choices(['1', '0'], weights=[0.40, 0.60])[0]
                        
                        observations.append({
                            'date': obs_date,
                            'class_code': class_to_observe,
                            'student_id': student['student_id'],
                            'measure_name': measure,
                            'value': value
                        })
    
    observations_df = pd.DataFrame(observations)
    
    return students_df, classes_df, observations_df


# ============================================================================
# ENGAGEMENT ANALYSIS METRICS
# ============================================================================

def calculate_effective_engagement(attendance_pct, achievement_pct):
    """
    Calculate Effective Engagement Score (EES)
    
    EES accounts for both attendance and achievement:
    A student who is 90% present and 50% engaged has different
    effective engagement than one who is 50% present and 90% engaged.
    
    Args:
        attendance_pct: Attendance percentage (0-100)
        achievement_pct: Achievement percentage (0-100)
    
    Returns:
        float: Effective Engagement Score (0-100)
    """
    if attendance_pct is None or achievement_pct is None:
        return 0.0
    return (attendance_pct * achievement_pct) / 100


def identify_primary_barrier(attendance_pct, achievement_pct, threshold=15):
    """
    Identify whether attendance or engagement is the primary barrier
    
    Args:
        attendance_pct: Attendance percentage (0-100)
        achievement_pct: Achievement percentage (0-100)
        threshold: Percentage difference threshold (default 15)
    
    Returns:
        str: "Attendance", "Engagement", or "Balanced"
    """
    if attendance_pct is None or achievement_pct is None:
        return "Unknown"
    
    diff = attendance_pct - achievement_pct
    
    if abs(diff) < threshold:
        return "Balanced"
    elif diff > threshold:
        return "Engagement"
    else:
        return "Attendance"


def classify_engagement_type(attendance_pct, achievement_pct):
    """
    Classify student into engagement type category
    
    Args:
        attendance_pct: Attendance percentage (0-100)
        achievement_pct: Achievement percentage (0-100)
    
    Returns:
        tuple: (category, emoji, description, intervention)
    """
    if attendance_pct is None or achievement_pct is None:
        return ("Unknown", "❓", "No data available", "Gather baseline data")
    
    # Define thresholds
    high_attendance = attendance_pct >= 80
    low_attendance = attendance_pct < 70
    high_achievement = achievement_pct >= 70
    low_achievement = achievement_pct < 60
    
    # Classification logic
    if high_attendance and high_achievement:
        return (
            "Exemplary",
            "⭐",
            "Consistently present and highly engaged",
            "Continue current strategies, consider leadership opportunities"
        )
    
    elif high_attendance and low_achievement:
        return (
            "Present but Disengaged",
            "⚠️",
            "Attending regularly but not engaging with material",
            "Focus on engagement strategies, check for understanding barriers"
        )
    
    elif low_attendance and high_achievement:
        return (
            "Engaged but Absent",
            "📚",
            "Highly engaged when present but poor attendance",
            "Address attendance barriers, explore alternative learning paths"
        )
    
    elif low_attendance and low_achievement:
        return (
            "Critical Intervention Needed",
            "🚨",
            "Both attendance and engagement are concerns",
            "Comprehensive support plan, family contact, counseling referral"
        )
    
    else:
        # Middle range
        if attendance_pct >= achievement_pct:
            return (
                "Developing - Focus Engagement",
                "📈",
                "Moderate attendance, needs engagement support",
                "Build on attendance strength, increase engagement"
            )
        else:
            return (
                "Developing - Focus Attendance",
                "📅",
                "Shows engagement when present, improve attendance",
                "Address attendance barriers while maintaining engagement"
            )


def calculate_opportunity_lost(attendance_pct, achievement_pct):
    """
    Calculate percentage of engagement opportunity lost due to absence
    
    Args:
        attendance_pct: Attendance percentage (0-100)
        achievement_pct: Achievement percentage (0-100)
    
    Returns:
        float: Percentage of potential engagement lost to absence
    """
    if attendance_pct is None or achievement_pct is None:
        return 0.0
    
    potential = achievement_pct  # What they could achieve if they attended
    actual = (attendance_pct * achievement_pct) / 100  # What they actually achieve
    lost = potential - actual
    
    return max(0.0, lost)  # Can't be negative


def get_engagement_correlation(observations_df, students_df):
    """
    Calculate correlation between attendance and achievement for a class
    
    Args:
        observations_df: DataFrame with observations
        students_df: DataFrame with students
    
    Returns:
        float: Correlation coefficient (-1 to 1)
    """
    if len(observations_df) == 0 or len(students_df) == 0:
        return 0.0
    
    student_metrics = []
    
    for _, student in students_df.iterrows():
        student_obs = observations_df[observations_df['student_id'] == student['student_id']]
        
        if len(student_obs) == 0:
            continue
        
        attendance_pct = calculate_attendance_rate(observations_df, student['student_id'])
        achievement_pct = calculate_performance(observations_df, student_id=student['student_id'])[0]
        
        if attendance_pct is not None and achievement_pct is not None:
            student_metrics.append({
                'attendance': attendance_pct,
                'achievement': achievement_pct
            })
    
    if len(student_metrics) < 2:
        return 0.0
    
    metrics_df = pd.DataFrame(student_metrics)
    correlation = metrics_df['attendance'].corr(metrics_df['achievement'])
    
    return correlation if not pd.isna(correlation) else 0.0


def get_class_engagement_distribution(observations_df, students_df):
    """
    Get distribution of students across engagement type categories
    
    Args:
        observations_df: DataFrame with observations
        students_df: DataFrame with students
    
    Returns:
        dict: Count of students in each category
    """
    distribution = {
        "Exemplary": 0,
        "Present but Disengaged": 0,
        "Engaged but Absent": 0,
        "Critical Intervention Needed": 0,
        "Developing - Focus Engagement": 0,
        "Developing - Focus Attendance": 0,
        "Unknown": 0
    }
    
    for _, student in students_df.iterrows():
        attendance_pct = calculate_attendance_rate(observations_df, student['student_id'])
        achievement_pct = calculate_performance(observations_df, student_id=student['student_id'])[0]
        
        category, _, _, _ = classify_engagement_type(attendance_pct, achievement_pct)
        distribution[category] += 1
    
    return distribution


def get_engagement_insights(observations_df, students_df):
    """
    Generate insights about engagement patterns in the class
    
    Args:
        observations_df: DataFrame with observations
        students_df: DataFrame with students
    
    Returns:
        dict: Various engagement insights
    """
    if len(observations_df) == 0 or len(students_df) == 0:
        return {
            'avg_effective_engagement': 0,
            'correlation': 0,
            'present_but_disengaged_count': 0,
            'engaged_but_absent_count': 0,
            'opportunity_lost_avg': 0,
            'primary_barrier_counts': {'Attendance': 0, 'Engagement': 0, 'Balanced': 0}
        }
    
    effective_engagements = []
    opportunities_lost = []
    primary_barriers = {'Attendance': 0, 'Engagement': 0, 'Balanced': 0, 'Unknown': 0}
    present_disengaged = 0
    engaged_absent = 0
    
    for _, student in students_df.iterrows():
        attendance_pct = calculate_attendance_rate(observations_df, student['student_id'])
        achievement_pct = calculate_performance(observations_df, student_id=student['student_id'])[0]
        
        if attendance_pct is not None and achievement_pct is not None:
            # Effective engagement
            ees = calculate_effective_engagement(attendance_pct, achievement_pct)
            effective_engagements.append(ees)
            
            # Opportunity lost
            lost = calculate_opportunity_lost(attendance_pct, achievement_pct)
            opportunities_lost.append(lost)
            
            # Primary barrier
            barrier = identify_primary_barrier(attendance_pct, achievement_pct)
            primary_barriers[barrier] += 1
            
            # Count specific patterns
            category, _, _, _ = classify_engagement_type(attendance_pct, achievement_pct)
            if category == "Present but Disengaged":
                present_disengaged += 1
            elif category == "Engaged but Absent":
                engaged_absent += 1
    
    return {
        'avg_effective_engagement': sum(effective_engagements) / len(effective_engagements) if effective_engagements else 0,
        'correlation': get_engagement_correlation(observations_df, students_df),
        'present_but_disengaged_count': present_disengaged,
        'engaged_but_absent_count': engaged_absent,
        'opportunity_lost_avg': sum(opportunities_lost) / len(opportunities_lost) if opportunities_lost else 0,
        'primary_barrier_counts': primary_barriers
    }

