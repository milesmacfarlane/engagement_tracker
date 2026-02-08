"""
Test script for Student Engagement Tracking System
Verifies core functionality without running the Streamlit UI
"""

import sys
import pandas as pd
from datetime import date, timedelta

# Import modules
import database as db
import utils

def test_sample_data_generation():
    """Test sample data generation"""
    print("=" * 60)
    print("TEST 1: Sample Data Generation")
    print("=" * 60)
    
    students_df, classes_df, observations_df = utils.create_sample_data()
    
    print(f"✓ Generated {len(students_df)} students")
    print(f"✓ Generated {len(classes_df)} classes")
    print(f"✓ Generated {len(observations_df)} observations")
    
    assert len(students_df) > 0, "Should have students"
    assert len(classes_df) == 3, "Should have 3 classes"
    assert len(observations_df) > 0, "Should have observations"
    
    print("\n✅ Sample data generation: PASSED\n")
    return students_df, classes_df, observations_df


def test_performance_calculations(observations_df):
    """Test performance calculation functions"""
    print("=" * 60)
    print("TEST 2: Performance Calculations")
    print("=" * 60)
    
    # Test overall performance calculation
    student_id = observations_df['student_id'].iloc[0]
    perf, ones, zeros, absent, valid = utils.calculate_performance(
        observations_df, student_id=student_id
    )
    
    print(f"Student {student_id}:")
    print(f"  Performance: {utils.format_percentage(perf)}")
    print(f"  Observed (1s): {ones}")
    print(f"  Not Observed (0s): {zeros}")
    print(f"  Absent (-): {absent}")
    print(f"  Valid Observations: {valid}")
    
    # Verify calculation
    if valid > 0:
        expected_perf = (ones / valid) * 100
        assert abs(perf - expected_perf) < 0.01, "Performance calculation incorrect"
    
    # Test performance band
    band_name, band_color = utils.get_performance_band(perf)
    print(f"  Band: {band_name}")
    
    print("\n✅ Performance calculations: PASSED\n")


def test_measure_breakdown(students_df, observations_df):
    """Test measure-by-measure breakdown"""
    print("=" * 60)
    print("TEST 3: Measure Breakdown")
    print("=" * 60)
    
    student_id = students_df['student_id'].iloc[0]
    breakdown = utils.get_student_measure_breakdown(observations_df, student_id)
    
    print(f"Student {student_id} - Measure Breakdown:")
    
    for item in breakdown[:3]:  # Show first 3 measures
        print(f"  {item['Measure']}: {utils.format_percentage(item['Performance %'])}")
    
    assert len(breakdown) == len(utils.ENGAGEMENT_MEASURES), "Should have all measures"
    
    print("\n✅ Measure breakdown: PASSED\n")


def test_top_and_bottom_measures(students_df, observations_df):
    """Test top strengths and improvement areas"""
    print("=" * 60)
    print("TEST 4: Top Strengths & Improvement Areas")
    print("=" * 60)
    
    student_id = students_df['student_id'].iloc[0]
    
    # Build measure performance dict
    measure_performance = {}
    for measure in utils.ENGAGEMENT_MEASURES:
        perf, _, _, _, _ = utils.calculate_performance(
            observations_df, student_id=student_id, measure=measure
        )
        measure_performance[measure] = perf
    
    # Get top measures
    top_measures = utils.get_top_measures(measure_performance, n=3)
    print(f"Top 3 Strengths for Student {student_id}:")
    for measure, perf in top_measures:
        print(f"  {measure}: {perf:.1f}%")
    
    # Get improvement areas
    improvement_areas = utils.get_improvement_areas(measure_performance, threshold=75, n=3)
    print(f"\nFocus Areas (below 75%):")
    if improvement_areas:
        for measure, perf in improvement_areas:
            print(f"  {measure}: {perf:.1f}%")
    else:
        print("  None - all measures above 75%")
    
    print("\n✅ Top/bottom measures: PASSED\n")


def test_class_summary(students_df, observations_df):
    """Test class performance summary"""
    print("=" * 60)
    print("TEST 5: Class Performance Summary")
    print("=" * 60)
    
    class_code = students_df['primary_class'].iloc[0]
    summary = utils.get_class_performance_summary(observations_df, students_df, class_code)
    
    print(f"Class {class_code} Summary:")
    print(f"  Total Students: {len(summary)}")
    
    students_with_data = [s for s in summary if s['Total Observations'] > 0]
    print(f"  Students with Observations: {len(students_with_data)}")
    
    if students_with_data:
        performances = [s['Performance %'] for s in students_with_data if s['Performance %'] is not None]
        if performances:
            avg_perf = sum(performances) / len(performances)
            print(f"  Class Average: {avg_perf:.1f}%")
    
    print("\n✅ Class summary: PASSED\n")


def test_database_operations():
    """Test database save/load operations"""
    print("=" * 60)
    print("TEST 6: Database Operations")
    print("=" * 60)
    
    # Clear existing data
    db.save_students(pd.DataFrame(columns=['student_id', 'name', 'primary_class']))
    db.save_classes(pd.DataFrame(columns=['class_code', 'class_name']))
    db.save_observations(pd.DataFrame(columns=['date', 'class_code', 'student_id', 'measure_name', 'value']))
    
    # Add a test class
    success = db.add_class("TEST101", "Test Class 101")
    assert success, "Should add class successfully"
    print("✓ Added test class")
    
    # Add a test student
    success = db.add_student("999999", "Test Student", "TEST101")
    assert success, "Should add student successfully"
    print("✓ Added test student")
    
    # Add test observations
    test_obs = [
        {
            'date': date.today(),
            'class_code': 'TEST101',
            'student_id': '999999',
            'measure_name': utils.ENGAGEMENT_MEASURES[0],
            'value': '1'
        }
    ]
    db.add_observations(test_obs)
    print("✓ Added test observation")
    
    # Verify data was saved and can be loaded
    students = db.load_students()
    classes = db.load_classes()
    observations = db.load_observations()
    
    assert len(students) > 0, "Should have students"
    assert len(classes) > 0, "Should have classes"
    assert len(observations) > 0, "Should have observations"
    
    print("✓ Loaded data successfully")
    
    print("\n✅ Database operations: PASSED\n")


def test_validation():
    """Test input validation"""
    print("=" * 60)
    print("TEST 7: Input Validation")
    print("=" * 60)
    
    # Test valid values
    assert utils.validate_observation_value('1'), "Should accept '1'"
    assert utils.validate_observation_value('0'), "Should accept '0'"
    assert utils.validate_observation_value('-'), "Should accept '-'"
    
    # Test invalid values
    assert not utils.validate_observation_value('2'), "Should reject '2'"
    assert not utils.validate_observation_value('x'), "Should reject 'x'"
    assert not utils.validate_observation_value(''), "Should reject empty string"
    
    print("✓ Validation working correctly")
    print("\n✅ Input validation: PASSED\n")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("STUDENT ENGAGEMENT TRACKER - SYSTEM TESTS")
    print("=" * 60 + "\n")
    
    try:
        # Generate sample data
        students_df, classes_df, observations_df = test_sample_data_generation()
        
        # Run tests
        test_performance_calculations(observations_df)
        test_measure_breakdown(students_df, observations_df)
        test_top_and_bottom_measures(students_df, observations_df)
        test_class_summary(students_df, observations_df)
        test_database_operations()
        test_validation()
        
        # Summary
        print("=" * 60)
        print("ALL TESTS PASSED! ✅")
        print("=" * 60)
        print("\nThe system is ready to use!")
        print("\nTo start the application, run:")
        print("  streamlit run app.py")
        print("=" * 60 + "\n")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("TEST FAILED! ❌")
        print("=" * 60)
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
