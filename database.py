"""
PostgreSQL Database Module for Neon.tech
Persistent cloud storage for student engagement data
"""

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from datetime import datetime
import os


def get_database_connection():
    """
    Get database connection from Streamlit secrets or environment
    
    Returns:
        sqlalchemy.engine.Engine or None
    """
    try:
        # Try to get from Streamlit secrets first
        if 'database_url' in st.secrets:
            database_url = st.secrets['database_url']
        # Fall back to environment variable
        elif 'DATABASE_URL' in os.environ:
            database_url = os.environ['DATABASE_URL']
        else:
            return None
        
        # Create engine
        engine = create_engine(database_url)
        return engine
    
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return None


def initialize_database():
    """
    Create tables if they don't exist
    
    Returns:
        bool: Success status
    """
    engine = get_database_connection()
    if not engine:
        return False
    
    try:
        with engine.connect() as conn:
            # Create students table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS students (
                    student_id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    primary_class VARCHAR(50) NOT NULL
                )
            """))
            
            # Create classes table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS classes (
                    class_code VARCHAR(50) PRIMARY KEY,
                    class_name VARCHAR(255) NOT NULL
                )
            """))
            
            # Create observations table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS observations (
                    id SERIAL PRIMARY KEY,
                    date DATE NOT NULL,
                    class_code VARCHAR(50) NOT NULL,
                    student_id VARCHAR(50) NOT NULL,
                    measure_name VARCHAR(255) NOT NULL,
                    value VARCHAR(10) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create index for faster queries
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_observations_student 
                ON observations(student_id)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_observations_date 
                ON observations(date, class_code)
            """))
            
            conn.commit()
        
        return True
    
    except Exception as e:
        st.error(f"Error initializing database: {str(e)}")
        return False


# ============================================================================
# STUDENTS
# ============================================================================

def load_students():
    """
    Load students from database
    
    Returns:
        pd.DataFrame: Students with columns [student_id, name, primary_class]
    """
    engine = get_database_connection()
    if not engine:
        return pd.DataFrame(columns=['student_id', 'name', 'primary_class'])
    
    try:
        query = "SELECT student_id, name, primary_class FROM students ORDER BY name"
        df = pd.read_sql(query, engine)
        df['student_id'] = df['student_id'].astype(str)
        return df
    
    except Exception as e:
        st.error(f"Error loading students: {str(e)}")
        return pd.DataFrame(columns=['student_id', 'name', 'primary_class'])


def save_students(students_df):
    """Save all students (replaces existing)"""
    engine = get_database_connection()
    if not engine:
        return False
    
    try:
        with engine.connect() as conn:
            # Clear existing students
            conn.execute(text("DELETE FROM students"))
            
            # Insert new students
            for _, row in students_df.iterrows():
                conn.execute(
                    text("""
                        INSERT INTO students (student_id, name, primary_class)
                        VALUES (:student_id, :name, :primary_class)
                    """),
                    {
                        'student_id': str(row['student_id']),
                        'name': row['name'],
                        'primary_class': row['primary_class']
                    }
                )
            
            conn.commit()
        return True
    
    except Exception as e:
        st.error(f"Error saving students: {str(e)}")
        return False


def add_student(student_id, name, primary_class):
    """Add a single student"""
    engine = get_database_connection()
    if not engine:
        return False
    
    try:
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO students (student_id, name, primary_class)
                    VALUES (:student_id, :name, :primary_class)
                    ON CONFLICT (student_id) DO UPDATE
                    SET name = :name, primary_class = :primary_class
                """),
                {
                    'student_id': str(student_id),
                    'name': name,
                    'primary_class': primary_class
                }
            )
            conn.commit()
        return True
    
    except Exception as e:
        st.error(f"Error adding student: {str(e)}")
        return False


def delete_student(student_id):
    """Delete a student"""
    engine = get_database_connection()
    if not engine:
        return False
    
    try:
        with engine.connect() as conn:
            conn.execute(
                text("DELETE FROM students WHERE student_id = :student_id"),
                {'student_id': str(student_id)}
            )
            conn.commit()
        return True
    
    except Exception as e:
        st.error(f"Error deleting student: {str(e)}")
        return False


def update_student(student_id, name, primary_class):
    """Update student information"""
    engine = get_database_connection()
    if not engine:
        return False
    
    try:
        with engine.connect() as conn:
            conn.execute(
                text("""
                    UPDATE students 
                    SET name = :name, primary_class = :primary_class
                    WHERE student_id = :student_id
                """),
                {
                    'student_id': str(student_id),
                    'name': name,
                    'primary_class': primary_class
                }
            )
            conn.commit()
        return True
    
    except Exception as e:
        st.error(f"Error updating student: {str(e)}")
        return False


# ============================================================================
# CLASSES
# ============================================================================

def load_classes():
    """Load classes from database"""
    engine = get_database_connection()
    if not engine:
        return pd.DataFrame(columns=['class_code', 'class_name'])
    
    try:
        query = "SELECT class_code, class_name FROM classes ORDER BY class_code"
        df = pd.read_sql(query, engine)
        return df
    
    except Exception as e:
        st.error(f"Error loading classes: {str(e)}")
        return pd.DataFrame(columns=['class_code', 'class_name'])


def save_classes(classes_df):
    """Save all classes"""
    engine = get_database_connection()
    if not engine:
        return False
    
    try:
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM classes"))
            
            for _, row in classes_df.iterrows():
                conn.execute(
                    text("""
                        INSERT INTO classes (class_code, class_name)
                        VALUES (:class_code, :class_name)
                    """),
                    {
                        'class_code': row['class_code'],
                        'class_name': row['class_name']
                    }
                )
            
            conn.commit()
        return True
    
    except Exception as e:
        st.error(f"Error saving classes: {str(e)}")
        return False


def add_class(class_code, class_name):
    """Add a single class"""
    engine = get_database_connection()
    if not engine:
        return False
    
    try:
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO classes (class_code, class_name)
                    VALUES (:class_code, :class_name)
                    ON CONFLICT (class_code) DO UPDATE
                    SET class_name = :class_name
                """),
                {
                    'class_code': class_code,
                    'class_name': class_name
                }
            )
            conn.commit()
        return True
    
    except Exception as e:
        st.error(f"Error adding class: {str(e)}")
        return False


def delete_class(class_code):
    """Delete a class"""
    engine = get_database_connection()
    if not engine:
        return False
    
    try:
        with engine.connect() as conn:
            conn.execute(
                text("DELETE FROM classes WHERE class_code = :class_code"),
                {'class_code': class_code}
            )
            conn.commit()
        return True
    
    except Exception as e:
        st.error(f"Error deleting class: {str(e)}")
        return False


# ============================================================================
# OBSERVATIONS
# ============================================================================

def load_observations():
    """Load observations from database"""
    engine = get_database_connection()
    if not engine:
        return pd.DataFrame(columns=['date', 'class_code', 'student_id', 'measure_name', 'value'])
    
    try:
        query = """
            SELECT date, class_code, student_id, measure_name, value
            FROM observations
            ORDER BY date DESC, class_code, student_id
        """
        df = pd.read_sql(query, engine)
        df['student_id'] = df['student_id'].astype(str)
        df['date'] = pd.to_datetime(df['date'])
        return df
    
    except Exception as e:
        st.error(f"Error loading observations: {str(e)}")
        return pd.DataFrame(columns=['date', 'class_code', 'student_id', 'measure_name', 'value'])


def save_observations(observations_df):
    """Save observations (not typically used - use add_observations instead)"""
    engine = get_database_connection()
    if not engine:
        return False
    
    try:
        # This would replace ALL observations - usually not desired
        # Keeping for compatibility but recommend using add_observations
        observations_df.to_sql('observations', engine, if_exists='replace', index=False)
        return True
    
    except Exception as e:
        st.error(f"Error saving observations: {str(e)}")
        return False


def add_observations(observations_list):
    """
    Add multiple observations efficiently
    
    Args:
        observations_list: List of dicts with keys [date, class_code, student_id, measure_name, value]
    """
    engine = get_database_connection()
    if not engine:
        return False
    
    try:
        with engine.connect() as conn:
            for obs in observations_list:
                conn.execute(
                    text("""
                        INSERT INTO observations (date, class_code, student_id, measure_name, value)
                        VALUES (:date, :class_code, :student_id, :measure_name, :value)
                    """),
                    {
                        'date': obs['date'],
                        'class_code': obs['class_code'],
                        'student_id': str(obs['student_id']),
                        'measure_name': obs['measure_name'],
                        'value': obs['value']
                    }
                )
            conn.commit()
        return True
    
    except Exception as e:
        st.error(f"Error adding observations: {str(e)}")
        return False


def delete_observations(observation_date, class_code):
    """Delete observations for specific date and class"""
    engine = get_database_connection()
    if not engine:
        return False
    
    try:
        with engine.connect() as conn:
            conn.execute(
                text("""
                    DELETE FROM observations 
                    WHERE date = :date AND class_code = :class_code
                """),
                {
                    'date': observation_date,
                    'class_code': class_code
                }
            )
            conn.commit()
        return True
    
    except Exception as e:
        st.error(f"Error deleting observations: {str(e)}")
        return False


# ============================================================================
# UTILITY
# ============================================================================

def ensure_data_dir():
    """No-op for PostgreSQL (kept for compatibility)"""
    pass


def initialize_sample_data():
    """Generate sample data"""
    import utils
    import random
    from datetime import date, timedelta
    
    # First, initialize database tables
    if not initialize_database():
        st.error("Failed to initialize database")
        return 0, 0, 0
    
    # Sample classes
    classes = [
        {'class_code': 'HIS20A', 'class_name': 'History 20 Section A'},
        {'class_code': 'HIS20B', 'class_name': 'History 20 Section B'},
        {'class_code': 'SST20', 'class_name': 'Social Studies 20'}
    ]
    classes_df = pd.DataFrame(classes)
    save_classes(classes_df)
    
    # Sample students
    first_names = ['Alice', 'Bob', 'Carol', 'David', 'Emma', 'Frank', 'Grace', 'Henry',
                   'Iris', 'Jack', 'Karen', 'Leo', 'Mary', 'Nathan', 'Olivia', 'Peter']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
    
    students = []
    student_id = 100000
    
    for class_code in ['HIS20A', 'HIS20B', 'SST20']:
        for i in range(20):
            students.append({
                'student_id': str(student_id),
                'name': f"{random.choice(first_names)} {random.choice(last_names)}",
                'primary_class': class_code
            })
            student_id += 1
    
    students_df = pd.DataFrame(students)
    save_students(students_df)
    
    # Sample observations
    observations = []
    today = date.today()
    
    for _ in range(10):
        obs_date = today - timedelta(days=random.randint(1, 30))
        
        for class_code in ['HIS20A', 'HIS20B', 'SST20']:
            class_students = students_df[students_df['primary_class'] == class_code]
            
            for _, student in class_students.iterrows():
                if random.random() < 0.9:  # 90% present
                    for measure in utils.ENGAGEMENT_MEASURES:
                        value = '1' if random.random() < 0.7 else '0'
                        observations.append({
                            'date': obs_date,
                            'class_code': class_code,
                            'student_id': student['student_id'],
                            'measure_name': measure,
                            'value': value
                        })
                else:  # Absent
                    for measure in utils.ENGAGEMENT_MEASURES:
                        observations.append({
                            'date': obs_date,
                            'class_code': class_code,
                            'student_id': student['student_id'],
                            'measure_name': measure,
                            'value': '-'
                        })
    
    add_observations(observations)
    
    return len(students), len(classes), len(observations)
