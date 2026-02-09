"""
Database operations for engagement tracking
Uses pandas DataFrames with CSV persistence for simplicity and portability
"""
import pandas as pd
import os
from datetime import datetime
import streamlit as st

DATA_DIR = 'data'
STUDENTS_FILE = os.path.join(DATA_DIR, 'students.csv')
CLASSES_FILE = os.path.join(DATA_DIR, 'classes.csv')
OBSERVATIONS_FILE = os.path.join(DATA_DIR, 'observations.csv')


def ensure_data_dir():
    """Ensure data directory exists"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def load_students():
    """
    Load students DataFrame
    
    Returns:
        pd.DataFrame: Students with columns [student_id, name, primary_class]
    """
    ensure_data_dir()
    
    if os.path.exists(STUDENTS_FILE):
        df = pd.read_csv(STUDENTS_FILE, dtype={'student_id': str})
        return df
    else:
        # Return empty DataFrame with correct schema
        return pd.DataFrame(columns=['student_id', 'name', 'primary_class'])


def save_students(students_df):
    """
    Save students DataFrame
    
    Args:
        students_df: DataFrame to save
    """
    ensure_data_dir()
    students_df.to_csv(STUDENTS_FILE, index=False)


def load_classes():
    """
    Load classes DataFrame
    
    Returns:
        pd.DataFrame: Classes with columns [class_code, class_name]
    """
    ensure_data_dir()
    
    if os.path.exists(CLASSES_FILE):
        df = pd.read_csv(CLASSES_FILE)
        return df
    else:
        # Return empty DataFrame with correct schema
        return pd.DataFrame(columns=['class_code', 'class_name'])


def save_classes(classes_df):
    """
    Save classes DataFrame
    
    Args:
        classes_df: DataFrame to save
    """
    ensure_data_dir()
    classes_df.to_csv(CLASSES_FILE, index=False)


def load_observations():
    """
    Load observations DataFrame
    
    Returns:
        pd.DataFrame: Observations with columns [date, class_code, student_id, measure_name, value]
    """
    ensure_data_dir()
    
    if os.path.exists(OBSERVATIONS_FILE):
        df = pd.read_csv(OBSERVATIONS_FILE, dtype={'student_id': str})
        # Handle different date formats flexibly
        try:
            df['date'] = pd.to_datetime(df['date'], format='ISO8601')
        except:
            try:
                df['date'] = pd.to_datetime(df['date'], format='mixed')
            except:
                df['date'] = pd.to_datetime(df['date'])
        return df
    else:
        # Return empty DataFrame with correct schema
        return pd.DataFrame(columns=['date', 'class_code', 'student_id', 'measure_name', 'value'])


def save_observations(observations_df):
    """
    Save observations DataFrame
    
    Args:
        observations_df: DataFrame to save
    """
    ensure_data_dir()
    # Create a copy and convert dates to string format for CSV storage
    df_to_save = observations_df.copy()
    if 'date' in df_to_save.columns and not df_to_save.empty:
        # Convert datetime to string format if needed
        if pd.api.types.is_datetime64_any_dtype(df_to_save['date']):
            df_to_save['date'] = df_to_save['date'].dt.strftime('%Y-%m-%d')
    df_to_save.to_csv(OBSERVATIONS_FILE, index=False)


def add_student(student_id, name, primary_class):
    """
    Add a new student
    
    Args:
        student_id: Student ID (string)
        name: Student name
        primary_class: Primary class code
    
    Returns:
        bool: True if successful, False if student already exists
    """
    students_df = load_students()
    
    # Check if student already exists
    if student_id in students_df['student_id'].values:
        return False
    
    # Add new student
    new_student = pd.DataFrame([{
        'student_id': student_id,
        'name': name,
        'primary_class': primary_class
    }])
    
    students_df = pd.concat([students_df, new_student], ignore_index=True)
    save_students(students_df)
    
    return True


def update_student(student_id, name=None, primary_class=None):
    """
    Update student information
    
    Args:
        student_id: Student ID
        name: New name (optional)
        primary_class: New primary class (optional)
    
    Returns:
        bool: True if successful, False if student not found
    """
    students_df = load_students()
    
    if student_id not in students_df['student_id'].values:
        return False
    
    if name is not None:
        students_df.loc[students_df['student_id'] == student_id, 'name'] = name
    
    if primary_class is not None:
        students_df.loc[students_df['student_id'] == student_id, 'primary_class'] = primary_class
    
    save_students(students_df)
    return True


def delete_student(student_id):
    """
    Delete a student and all their observations
    
    Args:
        student_id: Student ID
    
    Returns:
        bool: True if successful
    """
    students_df = load_students()
    students_df = students_df[students_df['student_id'] != student_id]
    save_students(students_df)
    
    # Also delete observations
    observations_df = load_observations()
    observations_df = observations_df[observations_df['student_id'] != student_id]
    save_observations(observations_df)
    
    return True


def add_class(class_code, class_name):
    """
    Add a new class
    
    Args:
        class_code: Class code (e.g., "HIS20A")
        class_name: Class name (e.g., "History 20 - Section A")
    
    Returns:
        bool: True if successful, False if class already exists
    """
    classes_df = load_classes()
    
    if class_code in classes_df['class_code'].values:
        return False
    
    new_class = pd.DataFrame([{
        'class_code': class_code,
        'class_name': class_name
    }])
    
    classes_df = pd.concat([classes_df, new_class], ignore_index=True)
    save_classes(classes_df)
    
    return True


def update_class(class_code, class_name):
    """
    Update class name
    
    Args:
        class_code: Class code
        class_name: New class name
    
    Returns:
        bool: True if successful
    """
    classes_df = load_classes()
    
    if class_code not in classes_df['class_code'].values:
        return False
    
    classes_df.loc[classes_df['class_code'] == class_code, 'class_name'] = class_name
    save_classes(classes_df)
    
    return True


def delete_class(class_code):
    """
    Delete a class
    
    Args:
        class_code: Class code
    
    Returns:
        bool: True if successful
    """
    classes_df = load_classes()
    classes_df = classes_df[classes_df['class_code'] != class_code]
    save_classes(classes_df)
    
    return True


def add_observations(observations_list):
    """
    Add multiple observations
    
    Args:
        observations_list: List of dicts with keys [date, class_code, student_id, measure_name, value]
    
    Returns:
        bool: True if successful
    """
    observations_df = load_observations()
    
    new_observations = pd.DataFrame(observations_list)
    
    # Ensure date is in consistent format
    if 'date' in new_observations.columns:
        new_observations['date'] = pd.to_datetime(new_observations['date']).dt.strftime('%Y-%m-%d')
    
    observations_df = pd.concat([observations_df, new_observations], ignore_index=True)
    
    save_observations(observations_df)
    
    return True


def delete_observations(date, class_code, student_id=None):
    """
    Delete observations for a specific date/class/student
    
    Args:
        date: Observation date
        class_code: Class code
        student_id: Optional student ID (if None, deletes for all students)
    
    Returns:
        bool: True if successful
    """
    observations_df = load_observations()
    
    # Filter out observations to delete
    mask = (observations_df['date'] == pd.to_datetime(date)) & \
           (observations_df['class_code'] == class_code)
    
    if student_id is not None:
        mask = mask & (observations_df['student_id'] == student_id)
    
    observations_df = observations_df[~mask]
    save_observations(observations_df)
    
    return True


def get_observation_dates():
    """
    Get list of unique observation dates
    
    Returns:
        list: Sorted list of dates
    """
    observations_df = load_observations()
    
    if len(observations_df) == 0:
        return []
    
    dates = pd.to_datetime(observations_df['date']).dt.date.unique()
    return sorted(dates, reverse=True)


def export_all_data(export_path):
    """
    Export all data to a directory
    
    Args:
        export_path: Path to export directory
    """
    import shutil
    
    if not os.path.exists(export_path):
        os.makedirs(export_path)
    
    # Copy all CSV files
    if os.path.exists(STUDENTS_FILE):
        shutil.copy(STUDENTS_FILE, os.path.join(export_path, 'students.csv'))
    
    if os.path.exists(CLASSES_FILE):
        shutil.copy(CLASSES_FILE, os.path.join(export_path, 'classes.csv'))
    
    if os.path.exists(OBSERVATIONS_FILE):
        shutil.copy(OBSERVATIONS_FILE, os.path.join(export_path, 'observations.csv'))


def import_data(import_path):
    """
    Import data from a directory
    
    Args:
        import_path: Path to import directory
    
    Returns:
        bool: True if successful
    """
    import shutil
    
    ensure_data_dir()
    
    # Copy all CSV files
    students_path = os.path.join(import_path, 'students.csv')
    if os.path.exists(students_path):
        shutil.copy(students_path, STUDENTS_FILE)
    
    classes_path = os.path.join(import_path, 'classes.csv')
    if os.path.exists(classes_path):
        shutil.copy(classes_path, CLASSES_FILE)
    
    observations_path = os.path.join(import_path, 'observations.csv')
    if os.path.exists(observations_path):
        shutil.copy(observations_path, OBSERVATIONS_FILE)
    
    return True


def initialize_sample_data():
    """
    Initialize database with sample data
    """
    from utils import create_sample_data
    
    students_df, classes_df, observations_df = create_sample_data()
    
    save_students(students_df)
    save_classes(classes_df)
    save_observations(observations_df)
