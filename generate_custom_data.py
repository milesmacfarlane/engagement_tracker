"""
Generate custom sample data with specific student profiles
January 2026 - 20 weekdays
"""

import pandas as pd
from datetime import date, timedelta
import random

# Student profiles
STUDENTS = [
    {
        'student_id': '1111111',
        'name': 'Student One',
        'primary_class': 'EMA40',
        'profile': 'poor_attender_unfocused',
        'attendance_rate': 0.40,  # 40% attendance
        'engagement_when_present': 0.25  # 25% engagement when present
    },
    {
        'student_id': '2222222',
        'name': 'Student Two',
        'primary_class': 'EMA40',
        'profile': 'poor_attender_struggling',
        'attendance_rate': 0.45,  # 45% attendance
        'engagement_when_present': 0.45  # 45% engagement when present (wants to but struggles)
    },
    {
        'student_id': '3333333',
        'name': 'Student Three',
        'primary_class': 'EMA40',
        'profile': 'moderate_coasting',
        'attendance_rate': 0.70,  # 70% attendance
        'engagement_when_present': 0.55  # 55% engagement (coasting)
    },
    {
        'student_id': '4444444',
        'name': 'Student Four',
        'primary_class': 'EMA40',
        'profile': 'moderate_anxious_helper',
        'attendance_rate': 0.70,  # 70% attendance
        'engagement_when_present': 0.75  # 75% engagement (does well, helps others)
    },
    {
        'student_id': '5555555',
        'name': 'Student Five',
        'primary_class': 'EMA40',
        'profile': 'good_attender_unfocused',
        'attendance_rate': 0.90,  # 90% attendance
        'engagement_when_present': 0.30  # 30% engagement (present but unfocused)
    },
    {
        'student_id': '6666666',
        'name': 'Student Six',
        'primary_class': 'EMA40',
        'profile': 'good_attender_coasting',
        'attendance_rate': 0.90,  # 90% attendance
        'engagement_when_present': 0.60  # 60% engagement (coasting on prior knowledge)
    },
    {
        'student_id': '7777777',
        'name': 'Student Seven',
        'primary_class': 'EMA40',
        'profile': 'good_attender_engaged',
        'attendance_rate': 0.95,  # 95% attendance
        'engagement_when_present': 0.88  # 88% engagement (does well)
    },
    {
        'student_id': '8888888',
        'name': 'Student Eight',
        'primary_class': 'EMA40',
        'profile': 'good_attender_minimalist',
        'attendance_rate': 0.90,  # 90% attendance
        'engagement_when_present': 0.65  # 65% engagement (does minimum, wastes time after)
    }
]

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

# Define behavior patterns for each profile
BEHAVIOR_PATTERNS = {
    'poor_attender_unfocused': {
        'Time on Task': 0.15,
        'Asked/Answered/Shared': 0.10,
        'Work Completed/Ready': 0.20,
        'Materials/Organized': 0.25,
        'Helping/Asking for Help': 0.15,
        'Asks for Clarification': 0.20,
        'Check-ins with Teacher': 0.30,
        'Asks for Ways to Improve': 0.10,
        'In-class Work Completed': 0.15
    },
    'poor_attender_struggling': {
        'Time on Task': 0.40,
        'Asked/Answered/Shared': 0.30,
        'Work Completed/Ready': 0.35,
        'Materials/Organized': 0.50,
        'Helping/Asking for Help': 0.60,  # Asks for help often
        'Asks for Clarification': 0.70,  # Wants to understand
        'Check-ins with Teacher': 0.50,
        'Asks for Ways to Improve': 0.55,  # Wants to improve
        'In-class Work Completed': 0.25   # Struggles to finish
    },
    'moderate_coasting': {
        'Time on Task': 0.50,
        'Asked/Answered/Shared': 0.45,
        'Work Completed/Ready': 0.70,  # Has prior knowledge
        'Materials/Organized': 0.60,
        'Helping/Asking for Help': 0.40,  # Doesn't need/offer much help
        'Asks for Clarification': 0.35,  # Doesn't ask much
        'Check-ins with Teacher': 0.40,
        'Asks for Ways to Improve': 0.30,  # Not motivated to improve
        'In-class Work Completed': 0.60
    },
    'moderate_anxious_helper': {
        'Time on Task': 0.75,
        'Asked/Answered/Shared': 0.70,
        'Work Completed/Ready': 0.80,
        'Materials/Organized': 0.85,  # Very organized
        'Helping/Asking for Help': 0.90,  # Helps others a lot
        'Asks for Clarification': 0.70,  # Anxious, asks questions
        'Check-ins with Teacher': 0.85,  # Checks in often (anxious)
        'Asks for Ways to Improve': 0.80,  # Wants to improve
        'In-class Work Completed': 0.75
    },
    'good_attender_unfocused': {
        'Time on Task': 0.25,  # Present but not focused
        'Asked/Answered/Shared': 0.20,
        'Work Completed/Ready': 0.30,
        'Materials/Organized': 0.40,
        'Helping/Asking for Help': 0.25,
        'Asks for Clarification': 0.20,
        'Check-ins with Teacher': 0.30,
        'Asks for Ways to Improve': 0.15,
        'In-class Work Completed': 0.30
    },
    'good_attender_coasting': {
        'Time on Task': 0.55,
        'Asked/Answered/Shared': 0.50,
        'Work Completed/Ready': 0.75,  # Prior knowledge helps
        'Materials/Organized': 0.65,
        'Helping/Asking for Help': 0.45,
        'Asks for Clarification': 0.40,
        'Check-ins with Teacher': 0.45,
        'Asks for Ways to Improve': 0.35,
        'In-class Work Completed': 0.65
    },
    'good_attender_engaged': {
        'Time on Task': 0.90,
        'Asked/Answered/Shared': 0.85,
        'Work Completed/Ready': 0.90,
        'Materials/Organized': 0.90,
        'Helping/Asking for Help': 0.85,
        'Asks for Clarification': 0.85,
        'Check-ins with Teacher': 0.90,
        'Asks for Ways to Improve': 0.85,
        'In-class Work Completed': 0.90
    },
    'good_attender_minimalist': {
        'Time on Task': 0.60,  # Focused when working, then wastes time
        'Asked/Answered/Shared': 0.55,
        'Work Completed/Ready': 0.80,  # Finishes quickly
        'Materials/Organized': 0.70,
        'Helping/Asking for Help': 0.50,
        'Asks for Clarification': 0.55,
        'Check-ins with Teacher': 0.60,
        'Asks for Ways to Improve': 0.45,
        'In-class Work Completed': 0.75  # Finishes fast, minimum effort
    }
}

def generate_custom_sample_data():
    """Generate sample data with specific student profiles"""
    
    # Classes
    classes = [
        {'class_code': 'EMA40', 'class_name': 'Essential Math (Grade 12, Period D)'}
    ]
    classes_df = pd.DataFrame(classes)
    
    # Students
    students_df = pd.DataFrame([
        {
            'student_id': s['student_id'],
            'name': s['name'],
            'primary_class': s['primary_class']
        }
        for s in STUDENTS
    ])
    
    # Generate 20 weekdays in January 2026
    observation_dates = []
    current_date = date(2026, 1, 2)  # First Friday of January 2026
    while len(observation_dates) < 20:
        if current_date.weekday() < 5:  # Monday=0, Friday=4
            observation_dates.append(current_date)
        current_date += timedelta(days=1)
    
    print(f"Generating observations for 20 weekdays in January 2026")
    print(f"Date range: {observation_dates[0]} to {observation_dates[-1]}")
    print()
    
    # Generate observations
    observations = []
    
    for student in STUDENTS:
        student_id = student['student_id']
        profile = student['profile']
        attendance_rate = student['attendance_rate']
        behavior_probs = BEHAVIOR_PATTERNS[profile]
        
        print(f"Generating data for {student['name']} ({student_id})")
        print(f"  Profile: {profile}")
        print(f"  Attendance rate: {attendance_rate*100:.0f}%")
        
        absent_count = 0
        present_count = 0
        
        for obs_date in observation_dates:
            # Determine if student is present
            is_present = random.random() < attendance_rate
            
            if not is_present:
                # Student is absent - all measures get "-"
                absent_count += 1
                for measure in ENGAGEMENT_MEASURES:
                    observations.append({
                        'date': obs_date,
                        'class_code': 'EMA40',
                        'student_id': student_id,
                        'measure_name': measure,
                        'value': '-'
                    })
            else:
                # Student is present - generate engagement observations
                present_count += 1
                for measure in ENGAGEMENT_MEASURES:
                    # Get probability for this measure
                    prob = behavior_probs[measure]
                    
                    # Add some randomness (±15%)
                    actual_prob = prob + random.uniform(-0.15, 0.15)
                    actual_prob = max(0, min(1, actual_prob))  # Clamp to 0-1
                    
                    # Determine if behavior was observed
                    value = '1' if random.random() < actual_prob else '0'
                    
                    observations.append({
                        'date': obs_date,
                        'class_code': 'EMA40',
                        'student_id': student_id,
                        'measure_name': measure,
                        'value': value
                    })
        
        print(f"  Present: {present_count} days, Absent: {absent_count} days")
        print()
    
    observations_df = pd.DataFrame(observations)
    
    return students_df, classes_df, observations_df


if __name__ == "__main__":
    print("=" * 70)
    print("CUSTOM SAMPLE DATA GENERATOR")
    print("=" * 70)
    print()
    
    students_df, classes_df, observations_df = generate_custom_sample_data()
    
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Students: {len(students_df)}")
    print(f"Classes: {len(classes_df)}")
    print(f"Observations: {len(observations_df)}")
    print(f"Date range: January 2-29, 2026 (20 weekdays)")
    print()
    
    # Save to CSV files
    print("Saving to data/ folder...")
    students_df.to_csv('data/students.csv', index=False)
    classes_df.to_csv('data/classes.csv', index=False)
    observations_df.to_csv('data/observations.csv', index=False)
    
    print("✅ Data saved successfully!")
    print()
    print("Files created:")
    print("  - data/students.csv")
    print("  - data/classes.csv")
    print("  - data/observations.csv")
    print()
    print("You can now launch the app and explore the data!")
    print("=" * 70)
