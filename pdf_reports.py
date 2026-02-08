"""
PDF Report Generation for Student Engagement Tracking System
Professional, greyscale-friendly reports for printing
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime, timedelta
import pandas as pd
import io
import utils
import database as db


def generate_student_report_pdf(student_id, date_range='ALL', start_date=None, end_date=None):
    """
    Generate a one-page PDF report for a student
    
    Args:
        student_id: Student ID
        date_range: 'ALL', 'MOST_RECENT', or 'DATE_RANGE'
        start_date: Start date for DATE_RANGE
        end_date: End date for DATE_RANGE
    
    Returns:
        BytesIO: PDF file buffer
    """
    # Load data
    students_df = db.load_students()
    observations_df = db.load_observations()
    
    # Get student info
    student = students_df[students_df['student_id'] == student_id].iloc[0]
    
    # Filter observations by date range
    observations_df = filter_observations_by_date(observations_df, date_range, start_date, end_date)
    
    # Filter for this student
    student_obs = observations_df[observations_df['student_id'] == student_id]
    
    # Create PDF buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.black,
        spaceAfter=6,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.black,
        spaceAfter=6,
        spaceBefore=8
    )
    normal_style = styles['Normal']
    
    # Title
    elements.append(Paragraph("STUDENT ENGAGEMENT REPORT", title_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Student Info
    info_data = [
        ['Student Name:', student['name'], 'Student ID:', student['student_id']],
        ['Primary Class:', student['primary_class'], 'Report Date:', datetime.now().strftime('%Y-%m-%d')]
    ]
    
    info_table = Table(info_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 1.5*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # Calculate statistics
    if len(student_obs) == 0:
        elements.append(Paragraph("No observations recorded for this student.", normal_style))
    else:
        # Overall achievement (performance)
        overall_perf, ones, zeros, absent, valid = utils.calculate_performance(
            student_obs, student_id=student_id
        )
        
        # Attendance rate (days present / total days)
        attendance_rate = utils.calculate_attendance_rate(observations_df, student_id)
        total_days = utils.get_total_observation_days(observations_df, student_id)
        days_absent = utils.get_days_absent(observations_df, student_id)
        days_present = total_days - days_absent
        
        # Performance Summary Box
        elements.append(Paragraph("PERFORMANCE SUMMARY", heading_style))
        
        band_name, _ = utils.get_performance_band(overall_perf)
        
        summary_data = [
            ['Attendance Rate:', utils.format_percentage(attendance_rate), 'Days Present:', f"{days_present}/{total_days}"],
            ['Achievement %:', utils.format_percentage(overall_perf), 'Performance Band:', band_name],
            ['Behaviors Observed (1s):', str(ones), 'Not Observed (0s):', str(zeros)],
            ['Days Absent:', str(days_absent), 'Valid Observations:', str(valid)]
        ]
        
        summary_table = Table(summary_data, colWidths=[1.8*inch, 1.5*inch, 1.8*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.15*inch))
        
        # Detailed Breakdown
        elements.append(Paragraph("ENGAGEMENT MEASURES - DETAILED BREAKDOWN", heading_style))
        
        breakdown = utils.get_student_measure_breakdown(student_obs, student_id)
        
        # Table header
        measure_data = [['Engagement Measure', 'Total', '1s', '0s', '-', 'Valid', 'Perf %', 'Band']]
        
        # Add data rows
        for item in breakdown:
            perf_str = utils.format_percentage(item['Performance %'])
            measure_data.append([
                item['Measure'],
                str(item['Total']),
                str(item['1s (Observed)']),
                str(item['0s (Not Observed)']),
                str(item['- (Absent)']),
                str(item['Valid Observations']),
                perf_str,
                item['Band']
            ])
        
        measure_table = Table(measure_data, colWidths=[2.2*inch, 0.5*inch, 0.4*inch, 0.4*inch, 0.4*inch, 0.5*inch, 0.6*inch, 1.6*inch])
        measure_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.8, 0.8, 0.8)),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(measure_table)
        elements.append(Spacer(1, 0.15*inch))
        
        # Top Strengths and Focus Areas
        measure_performance = {}
        for item in breakdown:
            if item['Performance %'] is not None and item['Performance %'] != 'N/A':
                # Get actual numeric value
                for b_item in breakdown:
                    if b_item['Measure'] == item['Measure']:
                        perf, _, _, _, _ = utils.calculate_performance(
                            student_obs, student_id=student_id, measure=item['Measure']
                        )
                        measure_performance[item['Measure']] = perf
                        break
        
        # Two columns for strengths and focus areas
        col_data = []
        
        # Top Strengths
        strengths_text = "<b>TOP STRENGTHS</b><br/>"
        top_measures = utils.get_top_measures(measure_performance, n=3)
        if top_measures:
            for i, (measure, perf) in enumerate(top_measures, 1):
                strengths_text += f"{i}. {measure} - {perf:.1f}%<br/>"
        else:
            strengths_text += "Insufficient data<br/>"
        
        # Focus Areas
        focus_text = "<b>FOCUS AREAS (Below 75%)</b><br/>"
        improvement_areas = utils.get_improvement_areas(measure_performance, threshold=75, n=3)
        if improvement_areas:
            for i, (measure, perf) in enumerate(improvement_areas, 1):
                focus_text += f"{i}. {measure} - {perf:.1f}%<br/>"
        else:
            focus_text += "All measures above 75%<br/>"
        
        col_data = [[Paragraph(strengths_text, normal_style), Paragraph(focus_text, normal_style)]]
        
        col_table = Table(col_data, colWidths=[3.5*inch, 3.5*inch])
        col_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(col_table)
        elements.append(Spacer(1, 0.1*inch))
        
        # Recommended Next Steps
        recommendations = utils.get_recommended_next_steps(overall_perf)
        elements.append(Paragraph("<b>RECOMMENDED NEXT STEPS</b>", normal_style))
        elements.append(Paragraph(recommendations, normal_style))
    
    # Date range footer
    elements.append(Spacer(1, 0.1*inch))
    date_range_text = get_date_range_text(date_range, start_date, end_date)
    elements.append(Paragraph(f"<i>Report Period: {date_range_text}</i>", normal_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer


def generate_class_report_pdf(class_codes, date_range='ALL', start_date=None, end_date=None):
    """
    Generate a class report PDF for one or more classes
    
    Args:
        class_codes: List of class codes or single class code
        date_range: 'ALL', 'MOST_RECENT', or 'DATE_RANGE'
        start_date: Start date for DATE_RANGE
        end_date: End date for DATE_RANGE
    
    Returns:
        BytesIO: PDF file buffer
    """
    # Ensure class_codes is a list
    if isinstance(class_codes, str):
        class_codes = [class_codes]
    
    # Load data
    students_df = db.load_students()
    classes_df = db.load_classes()
    observations_df = db.load_observations()
    
    # Filter observations by date range
    observations_df = filter_observations_by_date(observations_df, date_range, start_date, end_date)
    
    # Create PDF buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.black,
        spaceAfter=6,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=colors.black,
        spaceAfter=6,
        spaceBefore=8
    )
    normal_style = styles['Normal']
    small_style = ParagraphStyle(
        'Small',
        parent=styles['Normal'],
        fontSize=8
    )
    
    # Title
    if len(class_codes) == 1:
        class_name = classes_df[classes_df['class_code'] == class_codes[0]]['class_name'].values[0]
        title_text = f"CLASS ENGAGEMENT REPORT<br/>{class_codes[0]} - {class_name}"
    else:
        title_text = "CLASS ENGAGEMENT REPORT<br/>Multiple Classes"
    
    elements.append(Paragraph(title_text, title_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Report Info
    class_list = ', '.join(class_codes)
    info_data = [
        ['Classes:', class_list, 'Report Date:', datetime.now().strftime('%Y-%m-%d')]
    ]
    
    info_table = Table(info_data, colWidths=[1*inch, 4*inch, 1.5*inch, 1*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # Get combined class data
    class_students = students_df[students_df['primary_class'].isin(class_codes)]
    
    if len(class_students) == 0:
        elements.append(Paragraph("No students found in selected class(es).", normal_style))
    else:
        # Calculate class statistics
        total_students = len(class_students)
        
        # Get performance summary for all students
        all_summary = []
        for _, student in class_students.iterrows():
            perf, ones, zeros, absent, valid = utils.calculate_performance(
                observations_df, student_id=student['student_id']
            )
            if valid > 0:  # Only include students with valid observations
                all_summary.append({
                    'student_id': student['student_id'],
                    'name': student['name'],
                    'class': student['primary_class'],
                    'performance': perf
                })
        
        students_with_data = len(all_summary)
        
        # Calculate average
        if students_with_data > 0:
            class_avg = sum(s['performance'] for s in all_summary) / students_with_data
        else:
            class_avg = None
        
        # Overall Statistics
        elements.append(Paragraph("OVERALL CLASS STATISTICS", heading_style))
        
        stats_data = [
            ['Total Students:', str(total_students), 'Students Observed:', str(students_with_data)],
            ['Class Average:', utils.format_percentage(class_avg), '', '']
        ]
        
        stats_table = Table(stats_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        stats_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 0.15*inch))
        
        # Students by Performance Band
        elements.append(Paragraph("STUDENTS BY PERFORMANCE BAND", heading_style))
        
        # Group students by band
        band_groups = {}
        for band_info in utils.PERFORMANCE_BANDS:
            band_name = band_info[2]
            band_groups[band_name] = []
        band_groups["No Data"] = []
        
        for summary in all_summary:
            band_name, _ = utils.get_performance_band(summary['performance'])
            band_groups[band_name].append(summary['name'])
        
        # Students with no data
        for _, student in class_students.iterrows():
            if student['student_id'] not in [s['student_id'] for s in all_summary]:
                band_groups["No Data"].append(student['name'])
        
        # Create table with wrapped text
        band_data = [['Performance Band', 'Count', 'Students']]
        
        for band_info in utils.PERFORMANCE_BANDS:
            band_name = band_info[2]
            students = band_groups[band_name]
            count = len(students)
            student_list = ', '.join(students) if students else 'None'
            # Wrap student names in Paragraph for text wrapping
            student_paragraph = Paragraph(student_list, small_style)
            band_data.append([band_name, str(count), student_paragraph])
        
        # Add No Data
        no_data_students = band_groups["No Data"]
        no_data_list = ', '.join(no_data_students) if no_data_students else 'None'
        no_data_paragraph = Paragraph(no_data_list, small_style)
        band_data.append(["No Data", str(len(no_data_students)), no_data_paragraph])
        
        band_table = Table(band_data, colWidths=[1.5*inch, 0.7*inch, 4.8*inch])
        band_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.8, 0.8, 0.8)),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(band_table)
        
        # Add page break before next section
        elements.append(PageBreak())
        
        # Engagement Measures - Students Needing Attention
        elements.append(Paragraph("STUDENTS NEEDING ATTENTION BY MEASURE (Below 75%)", heading_style))
        
        measure_data = [['Engagement Measure', 'Avg %', 'Students Below 75%']]
        
        for measure in utils.ENGAGEMENT_MEASURES:
            # Get all students' performance for this measure
            measure_perfs = []
            students_below = []
            
            for _, student in class_students.iterrows():
                perf, _, _, _, valid = utils.calculate_performance(
                    observations_df, student_id=student['student_id'], measure=measure
                )
                if valid > 0:
                    measure_perfs.append(perf)
                    if perf < 75:
                        students_below.append(f"{student['name']} ({perf:.0f}%)")
            
            avg_perf = sum(measure_perfs) / len(measure_perfs) if measure_perfs else None
            students_text = ', '.join(students_below) if students_below else 'None'
            # Wrap in Paragraph for text wrapping
            students_paragraph = Paragraph(students_text, small_style)
            
            measure_data.append([
                measure,
                utils.format_percentage(avg_perf),
                students_paragraph
            ])
        
        measure_table = Table(measure_data, colWidths=[2.2*inch, 0.8*inch, 4*inch])
        measure_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.8, 0.8, 0.8)),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(measure_table)
    
    # Date range footer
    elements.append(Spacer(1, 0.1*inch))
    date_range_text = get_date_range_text(date_range, start_date, end_date)
    elements.append(Paragraph(f"<i>Report Period: {date_range_text}</i>", normal_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer


def filter_observations_by_date(observations_df, date_range, start_date=None, end_date=None):
    """Filter observations by date range"""
    if date_range == 'ALL':
        return observations_df
    
    elif date_range == 'MOST_RECENT':
        # Last 30 days
        cutoff_date = datetime.now().date() - timedelta(days=30)
        observations_df = observations_df.copy()
        observations_df['date'] = pd.to_datetime(observations_df['date'])
        return observations_df[observations_df['date'].dt.date >= cutoff_date]
    
    elif date_range == 'DATE_RANGE':
        if start_date and end_date:
            observations_df = observations_df.copy()
            observations_df['date'] = pd.to_datetime(observations_df['date'])
            return observations_df[
                (observations_df['date'].dt.date >= start_date) &
                (observations_df['date'].dt.date <= end_date)
            ]
        else:
            return observations_df
    
    return observations_df


def get_date_range_text(date_range, start_date, end_date):
    """Get human-readable date range text"""
    if date_range == 'ALL':
        return "All observations"
    elif date_range == 'MOST_RECENT':
        cutoff = (datetime.now().date() - timedelta(days=30)).strftime('%Y-%m-%d')
        return f"Last 30 days (since {cutoff})"
    elif date_range == 'DATE_RANGE':
        if start_date and end_date:
            return f"{start_date} to {end_date}"
        else:
            return "Custom date range"
    return "Unknown"
