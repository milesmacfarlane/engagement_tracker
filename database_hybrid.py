"""
Hybrid Database Module - Supports both CSV (local) and Google Sheets (cloud)
Automatically uses Google Sheets if connected, otherwise falls back to CSV
"""

import pandas as pd
import os
from datetime import datetime
import streamlit as st

# Import Google Sheets integration
try:
    import google_sheets_integration as gsheets
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False
    gsheets = None

# Data directory for CSV fallback
DATA_DIR = 'data'
STUDENTS_FILE = os.path.join(DATA_DIR, 'students.csv')
CLASSES_FILE = os.path.join(DATA_DIR, 'classes.csv')
OBSERVATIONS_FILE = os.path.join(DATA_DIR, 'observations.csv')


def is_using_google_sheets():
    """Check if Google Sheets is connected and available"""
    return (GSHEETS_AVAILABLE and 
            st.session_state.get('google_sheets_connected', False) and
            st.session_state.get('google_sheet_url', None))


def ensure_data_dir():
    """Ensure data directory exists (for CSV fallback)"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


# ============================================================================
# STUDENTS
# ============================================================================

def load_students():
    """
    Load students DataFrame from Google Sheets or CSV
    
    Returns:
        pd.DataFrame: Students with columns [student_id, name, primary_class]
    """
    if is_using_google_sheets():
        df = gsheets.load_sheet_data('students')
        if df is not None:
            # Ensure correct dtypes
            if len(df) > 0 and 'student_id' in df.columns:
                df['student_id'] = df['student_id'].astype(str)
            return df
    
    # Fallback to CSV
    ensure_data_dir()
    if os.path.exists(STUDENTS_FILE):
        df = pd.read_csv(STUDENTS_FILE, dtype={'student_id': str})
        return df
    else:
        return pd.DataFrame(columns=['student_id', 'name', 'primary_class'])


def save_students(students_df):
    """Save students DataFrame to Google Sheets or CSV"""
    if is_using_google_sheets():
        return gsheets.save_sheet_data('students', students_df)
    else:
        ensure_data_dir()
        students_df.to_csv(STUDENTS_FILE, index=False)
        return True


def add_student(student_id, name, primary_class):
    """Add a single student"""
    students_df = load_students()
    
    new_student = pd.DataFrame([{
        'student_id': str(student_id),
        'name': name,
        'primary_class': primary_class
    }])
    
    students_df = pd.concat([students_df, new_student], ignore_index=True)
    return save_students(students_df)


def delete_student(student_id):
    """Delete a student"""
    students_df = load_students()
    students_df = students_df[students_df['student_id'] != str(student_id)]
    return save_students(students_df)


def update_student(student_id, name, primary_class):
    """Update student information"""
    students_df = load_students()
    mask = students_df['student_id'] == str(student_id)
    students_df.loc[mask, 'name'] = name
    students_df.loc[mask, 'primary_class'] = primary_class
    return save_students(students_df)


# ============================================================================
# CLASSES
# ============================================================================

def load_classes():
    """
    Load classes DataFrame from Google Sheets or CSV
    
    Returns:
        pd.DataFrame: Classes with columns [class_code, class_name]
    """
    if is_using_google_sheets():
        df = gsheets.load_sheet_data('classes')
        if df is not None:
            return df
    
    # Fallback to CSV
    ensure_data_dir()
    if os.path.exists(CLASSES_FILE):
        return pd.read_csv(CLASSES_FILE)
    else:
        return pd.DataFrame(columns=['class_code', 'class_name'])


def save_classes(classes_df):
    """Save classes DataFrame to Google Sheets or CSV"""
    if is_using_google_sheets():
        return gsheets.save_sheet_data('classes', classes_df)
    else:
        ensure_data_dir()
        classes_df.to_csv(CLASSES_FILE, index=False)
        return True


def add_class(class_code, class_name):
    """Add a single class"""
    classes_df = load_classes()
    
    new_class = pd.DataFrame([{
        'class_code': class_code,
        'class_name': class_name
    }])
    
    classes_df = pd.concat([classes_df, new_class], ignore_index=True)
    return save_classes(classes_df)


def delete_class(class_code):
    """Delete a class"""
    classes_df = load_classes()
    classes_df = classes_df[classes_df['class_code'] != class_code]
    return save_classes(classes_df)


# ============================================================================
# OBSERVATIONS
# ============================================================================

def load_observations():
    """
    Load observations DataFrame from Google Sheets or CSV
    
    Returns:
        pd.DataFrame: Observations with columns [date, class_code, student_id, measure_name, value]
    """
    if is_using_google_sheets():
        df = gsheets.load_sheet_data('observations')
        if df is not None and len(df) > 0:
            # Ensure correct dtypes
            if 'student_id' in df.columns:
                df['student_id'] = df['student_id'].astype(str)
            if 'date' in df.columns:
                # Handle date parsing
                try:
                    df['date'] = pd.to_datetime(df['date'], format='ISO8601')
                except:
                    try:
                        df['date'] = pd.to_datetime(df['date'], format='mixed')
                    except:
                        df['date'] = pd.to_datetime(df['date'])
            return df
    
    # Fallback to CSV
    ensure_data_dir()
    if os.path.exists(OBSERVATIONS_FILE):
        df = pd.read_csv(OBSERVATIONS_FILE, dtype={'student_id': str})
        # Handle date parsing
        try:
            df['date'] = pd.to_datetime(df['date'], format='ISO8601')
        except:
            try:
                df['date'] = pd.to_datetime(df['date'], format='mixed')
            except:
                df['date'] = pd.to_datetime(df['date'])
        return df
    else:
        return pd.DataFrame(columns=['date', 'class_code', 'student_id', 'measure_name', 'value'])


def save_observations(observations_df):
    """Save observations DataFrame to Google Sheets or CSV"""
    # Create a copy and convert dates to string format for storage
    df_to_save = observations_df.copy()
    if 'date' in df_to_save.columns and not df_to_save.empty:
        # Convert datetime to string format if needed
        if pd.api.types.is_datetime64_any_dtype(df_to_save['date']):
            df_to_save['date'] = df_to_save['date'].dt.strftime('%Y-%m-%d')
    
    if is_using_google_sheets():
        return gsheets.save_sheet_data('observations', df_to_save)
    else:
        ensure_data_dir()
        df_to_save.to_csv(OBSERVATIONS_FILE, index=False)
        return True


def add_observations(observations_list):
    """
    Add multiple observations (more efficient for batch insert)
    
    Args:
        observations_list: List of dicts with keys [date, class_code, student_id, measure_name, value]
    
    Returns:
        bool: Success status
    """
    observations_df = load_observations()
    
    new_observations = pd.DataFrame(observations_list)
    
    # Ensure date is in consistent format
    if 'date' in new_observations.columns:
        new_observations['date'] = pd.to_datetime(new_observations['date']).dt.strftime('%Y-%m-%d')
    
    observations_df = pd.concat([observations_df, new_observations], ignore_index=True)
    
    return save_observations(observations_df)


def delete_observations(observation_date, class_code):
    """
    Delete all observations for a specific date and class
    
    Args:
        observation_date: Date to delete
        class_code: Class code
    
    Returns:
        bool: Success status
    """
    observations_df = load_observations()
    
    mask = (pd.to_datetime(observations_df['date']).dt.date != observation_date) | \
           (observations_df['class_code'] != class_code)
    
    observations_df = observations_df[mask]
    
    return save_observations(observations_df)


# ============================================================================
# SAMPLE DATA GENERATION
# ============================================================================

def initialize_sample_data():
    """Generate sample data for testing"""
    import utils
    import random
    from datetime import date, timedelta
    
    # Sample classes
    classes = [
        {'class_code': 'HIS20A', 'class_name': 'History 20 Section A'},
        {'class_code': 'HIS20B', 'class_name': 'History 20 Section B'},
        {'class_code': 'SST20', 'class_name': 'Social Studies 20'}
    ]
    classes_df = pd.DataFrame(classes)
    save_classes(classes_df)
    
    # Sample students (20-25 per class)
    first_names = ['Alice', 'Bob', 'Carol', 'David', 'Emma', 'Frank', 'Grace', 'Henry',
                   'Iris', 'Jack', 'Karen', 'Leo', 'Mary', 'Nathan', 'Olivia', 'Peter',
                   'Quinn', 'Rachel', 'Sam', 'Tina', 'Uma', 'Victor', 'Wendy', 'Xavier', 'Yara', 'Zack']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
                  'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
                  'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin']
    
    students = []
    student_id = 100000
    
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
    save_students(students_df)
    
    # Sample observations (10 random dates in past month)
    observations = []
    today = date.today()
    
    for _ in range(10):
        obs_date = today - timedelta(days=random.randint(1, 30))
        
        for class_code in ['HIS20A', 'HIS20B', 'SST20']:
            class_students = students_df[students_df['primary_class'] == class_code]
            
            for _, student in class_students.iterrows():
                # Random attendance (90% present)
                if random.random() < 0.9:
                    # Present - record observations
                    for measure in utils.ENGAGEMENT_MEASURES:
                        # Random performance (70% observed)
                        value = '1' if random.random() < 0.7 else '0'
                        observations.append({
                            'date': obs_date,
                            'class_code': class_code,
                            'student_id': student['student_id'],
                            'measure_name': measure,
                            'value': value
                        })
                else:
                    # Absent - all measures marked with '-'
                    for measure in utils.ENGAGEMENT_MEASURES:
                        observations.append({
                            'date': obs_date,
                            'class_code': class_code,
                            'student_id': student['student_id'],
                            'measure_name': measure,
                            'value': '-'
                        })
    
    observations_df = pd.DataFrame(observations)
    save_observations(observations_df)
    
    return len(students), len(classes), len(observations)
