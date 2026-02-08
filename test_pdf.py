"""
Test PDF Report Generation
"""

import sys
import database as db
import pdf_reports
from datetime import date

print("=" * 60)
print("PDF REPORT GENERATION TEST")
print("=" * 60)

# Initialize sample data
print("\n1. Loading sample data...")
db.initialize_sample_data()

students_df = db.load_students()
classes_df = db.load_classes()
observations_df = db.load_observations()

print(f"   ✓ Loaded {len(students_df)} students")
print(f"   ✓ Loaded {len(classes_df)} classes")
print(f"   ✓ Loaded {len(observations_df)} observations")

# Test student report
print("\n2. Testing Student Report PDF generation...")
student_id = students_df['student_id'].iloc[0]
student_name = students_df['name'].iloc[0]

try:
    pdf_buffer = pdf_reports.generate_student_report_pdf(
        student_id,
        date_range='ALL'
    )
    
    # Save to file
    with open('/tmp/test_student_report.pdf', 'wb') as f:
        f.write(pdf_buffer.getvalue())
    
    print(f"   ✓ Generated student report for {student_name}")
    print(f"   ✓ Saved to: /tmp/test_student_report.pdf")
    print(f"   ✓ File size: {len(pdf_buffer.getvalue())} bytes")
    
except Exception as e:
    print(f"   ✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test class report
print("\n3. Testing Class Report PDF generation...")
class_code = classes_df['class_code'].iloc[0]

try:
    pdf_buffer = pdf_reports.generate_class_report_pdf(
        [class_code],
        date_range='ALL'
    )
    
    # Save to file
    with open('/tmp/test_class_report.pdf', 'wb') as f:
        f.write(pdf_buffer.getvalue())
    
    print(f"   ✓ Generated class report for {class_code}")
    print(f"   ✓ Saved to: /tmp/test_class_report.pdf")
    print(f"   ✓ File size: {len(pdf_buffer.getvalue())} bytes")
    
except Exception as e:
    print(f"   ✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test multi-class report
print("\n4. Testing Multi-Class Report PDF generation...")
all_classes = classes_df['class_code'].tolist()

try:
    pdf_buffer = pdf_reports.generate_class_report_pdf(
        all_classes,
        date_range='MOST_RECENT'
    )
    
    # Save to file
    with open('/tmp/test_multiclass_report.pdf', 'wb') as f:
        f.write(pdf_buffer.getvalue())
    
    print(f"   ✓ Generated multi-class report for {len(all_classes)} classes")
    print(f"   ✓ Saved to: /tmp/test_multiclass_report.pdf")
    print(f"   ✓ File size: {len(pdf_buffer.getvalue())} bytes")
    
except Exception as e:
    print(f"   ✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL PDF TESTS PASSED! ✅")
print("=" * 60)
print("\nGenerated test PDFs:")
print("  - /tmp/test_student_report.pdf")
print("  - /tmp/test_class_report.pdf")
print("  - /tmp/test_multiclass_report.pdf")
print("\nPDF generation is working correctly!")
print("=" * 60 + "\n")
