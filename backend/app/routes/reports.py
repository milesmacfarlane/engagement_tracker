"""Report generation routes."""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, HRFlowable
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Line, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from datetime import datetime
import tempfile
import os

from app.database import get_session
from app.models import Student, Class
from app.services import CalculationService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/student/{student_id}")
async def generate_student_report(
    student_id: str,
    format: str = Query("pdf", regex="^(pdf|html)$"),
    session: AsyncSession = Depends(get_session)
):
    """Generate student report (PDF or HTML)."""
    # Verify student exists
    query = select(Student).where(Student.student_id == student_id)
    result = await session.execute(query)
    student = result.scalar_one_or_none()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if format == "html":
        # Return JSON representation for frontend to render
        overall_perf, _, _, _, _ = await CalculationService.calculate_performance(
            session, student_id=student_id
        )
        measure_breakdown = await CalculationService.get_student_measure_breakdown(session, student_id)
        attendance = await CalculationService.calculate_attendance_rate(session, student_id)
        band_name, _ = CalculationService.get_performance_band(overall_perf)
        next_steps = CalculationService.get_recommended_next_steps(overall_perf)

        return {
            "student_id": student_id,
            "student_name": student.name,
            "class": student.primary_class,
            "generated_at": datetime.now().isoformat(),
            "overall_performance": CalculationService.format_percentage(overall_perf),
            "performance_band": band_name,
            "attendance_rate": CalculationService.format_percentage(attendance),
            "measures": measure_breakdown,
            "recommended_next_steps": next_steps
        }

    else:  # PDF
        try:
            # Get analytics data
            overall_perf, ones, zeros, _, _ = await CalculationService.calculate_performance(
                session, student_id=student_id
            )
            measure_breakdown = await CalculationService.get_student_measure_breakdown(session, student_id)
            attendance = await CalculationService.calculate_attendance_rate(session, student_id)
            days_observed = await CalculationService.get_total_observation_days(session, student_id)
            days_absent = await CalculationService.get_days_absent(session, student_id)

            has_data = overall_perf is not None and overall_perf > 0

            if has_data:
                band_name, _ = CalculationService.get_performance_band(overall_perf)
                next_steps = CalculationService.get_recommended_next_steps(overall_perf)
            else:
                band_name = "N/A"
                next_steps = "No observation data available for this student."

            # Create PDF in memory
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=colors.black,
                spaceAfter=12,
                alignment=1  # Center
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=colors.black,
                spaceAfter=10,
                fontName='Helvetica-Bold'
            )

            story = []

            # Title
            story.append(Paragraph("STUDENT ENGAGEMENT REPORT", title_style))
            story.append(Spacer(1, 0.15*inch))

            # Header info table
            header_data = [
                ["Student Name:", student.name, "Student ID:", student.student_id],
                ["Primary Class:", student.primary_class, "Report Date:", datetime.now().strftime('%Y-%m-%d')]
            ]
            header_table = Table(header_data, colWidths=[1.2*inch, 2*inch, 1.2*inch, 2*inch])
            header_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            story.append(header_table)
            story.append(Spacer(1, 0.2*inch))

            # Performance Summary
            story.append(Paragraph("PERFORMANCE SUMMARY", heading_style))

            perf_summary = [
                ["Attendance Rate:", CalculationService.format_percentage(attendance), "Days Present:", f"{days_observed}/{days_observed + days_absent}"],
                ["Achievement %:", CalculationService.format_percentage(overall_perf), "Performance Band:", band_name],
                ["Behaviors Observed (1s):", str(ones or 0), "Not Observed (0s):", str(zeros or 0)],
                ["Days Absent:", str(days_absent or 0), "Valid Observations:", str((ones or 0) + (zeros or 0))]
            ]

            perf_table = Table(perf_summary, colWidths=[1.8*inch, 1.2*inch, 1.8*inch, 1.2*inch])
            perf_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
            ]))
            story.append(perf_table)
            story.append(Spacer(1, 0.2*inch))

            # Engagement Measures - Detailed Breakdown
            story.append(Paragraph("ENGAGEMENT MEASURES - DETAILED BREAKDOWN", heading_style))

            if not has_data or not measure_breakdown:
                story.append(Paragraph(
                    "<i>No observation data available. No performance measurements to display.</i>",
                    styles['Normal']
                ))
            else:
                try:
                    # Create detailed measure table matching Streamlit format
                    measure_data = [[
                        Paragraph("<b>Engagement Measure</b>", styles['Normal']),
                        Paragraph("<b>Total</b>", styles['Normal']),
                        Paragraph("<b>1s</b>", styles['Normal']),
                        Paragraph("<b>0s</b>", styles['Normal']),
                        Paragraph("<b>N/A</b>", styles['Normal']),
                        Paragraph("<b>Valid</b>", styles['Normal']),
                        Paragraph("<b>Perf %</b>", styles['Normal']),
                        Paragraph("<b>Band</b>", styles['Normal'])
                    ]]

                    for m in measure_breakdown:
                        perf_pct = m.get('performance_percentage', 0) or 0
                        band = m.get('band', 'N/A')
                        ones_obs = m.get('ones_observed', 0)
                        zeros_obs = m.get('zeros_not_observed', 0)
                        not_applicable = m.get('not_applicable', 0)
                        total = ones_obs + zeros_obs + not_applicable

                        measure_data.append([
                            Paragraph(m.get('measure', 'Unknown'), styles['Normal']),
                            Paragraph(str(total), styles['Normal']),
                            Paragraph(str(ones_obs), styles['Normal']),
                            Paragraph(str(zeros_obs), styles['Normal']),
                            Paragraph(str(not_applicable), styles['Normal']),
                            Paragraph(str(ones_obs + zeros_obs), styles['Normal']),
                            Paragraph(f"{perf_pct:.1f}%", styles['Normal']),
                            Paragraph(band, styles['Normal'])
                        ])

                    measure_table = Table(measure_data, colWidths=[2.2*inch, 0.45*inch, 0.45*inch, 0.45*inch, 0.45*inch, 0.5*inch, 0.55*inch, 1*inch])

                    # Professional styling
                    style_list = [
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#808080')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTNAME', (-1, 1), (-1, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('LEFTPADDING', (0, 0), (0, -1), 6),
                        ('RIGHTPADDING', (-1, 0), (-1, -1), 6),
                        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
                    ]

                    measure_table.setStyle(TableStyle(style_list))
                    story.append(measure_table)
                except Exception as e:
                    logger.error(f"Error creating measure table: {str(e)}", exc_info=True)
                    story.append(Paragraph(
                        f"<i>Could not display measure breakdown: {str(e)}</i>",
                        styles['Normal']
                    ))

            story.append(Spacer(1, 0.2*inch))

            # Performance by Measure Chart
            if has_data and measure_breakdown:
                story.append(Paragraph("PERFORMANCE BY MEASURE", heading_style))
                try:
                    # Create bar chart for measures
                    perf_drawing = Drawing(6.5*inch, 2.2*inch)
                    perf_chart = VerticalBarChart()

                    measure_names = [m.get('measure', 'Unknown')[:15] for m in measure_breakdown]
                    measure_perfs = [m.get('performance_percentage', 0) or 0 for m in measure_breakdown]

                    perf_chart.data = [measure_perfs]
                    perf_chart.categoryAxis.categoryNames = measure_names
                    perf_chart.categoryAxis.labels.angle = 45
                    perf_chart.categoryAxis.labels.fontSize = 8
                    perf_chart.valueAxis.valueMax = 100
                    perf_chart.valueAxis.valueMin = 0
                    perf_chart.width = 5.8*inch
                    perf_chart.height = 2*inch
                    perf_chart.x = 0.4*inch
                    perf_chart.y = 0.1*inch

                    # Color bars based on performance
                    perf_chart.bars[0].fillColor = colors.HexColor('#3b82f6')

                    perf_drawing.add(perf_chart)
                    story.append(perf_drawing)
                    story.append(Spacer(1, 0.2*inch))
                except Exception as e:
                    logger.error(f"Error creating performance chart: {str(e)}", exc_info=True)
                    story.append(Paragraph(f"<i>Could not display chart</i>", styles['Normal']))
                    story.append(Spacer(1, 0.2*inch))

            # Attendance Breakdown Chart
            if has_data and days_observed > 0:
                story.append(Paragraph("ATTENDANCE BREAKDOWN", heading_style))
                try:
                    att_drawing = Drawing(4*inch, 2.5*inch)
                    att_pie = Pie()

                    att_pie.data = [days_observed, days_absent]
                    att_pie.labels = [f"Present\n({days_observed})", f"Absent\n({days_absent})"]
                    att_pie.width = 3.5*inch
                    att_pie.height = 2.2*inch
                    att_pie.x = 0.2*inch
                    att_pie.y = 0.1*inch

                    att_pie.slices.strokeWidth = 1
                    att_pie.slices.strokeColor = colors.white
                    att_pie.slices[0].fillColor = colors.HexColor('#10b981')
                    att_pie.slices[1].fillColor = colors.HexColor('#ef4444')

                    att_drawing.add(att_pie)
                    story.append(att_drawing)
                    story.append(Spacer(1, 0.2*inch))
                except Exception as e:
                    logger.error(f"Error creating attendance chart: {str(e)}", exc_info=True)
                    story.append(Paragraph(f"<i>Could not display chart</i>", styles['Normal']))
                    story.append(Spacer(1, 0.2*inch))

            # Top Strengths and Focus Areas
            if has_data and measure_breakdown:
                try:
                    # Sort measures by performance
                    sorted_measures = sorted(measure_breakdown, key=lambda x: x.get('performance_percentage', 0) or 0, reverse=True)

                    # Top strengths (top 3)
                    top_strengths = sorted_measures[:3]

                    # Focus areas (below 75%)
                    focus_areas = [m for m in sorted_measures if (m.get('performance_percentage', 0) or 0) < 75]

                    two_col_data = []

                    # Left column: Top Strengths
                    left_content = ["TOP STRENGTHS"]
                    for idx, m in enumerate(top_strengths, 1):
                        perf_pct = m.get('performance_percentage', 0) or 0
                        left_content.append(f"{idx}. {m.get('measure', 'Unknown')} - {perf_pct:.1f}%")

                    # Right column: Focus Areas
                    right_content = ["FOCUS AREAS (Below 75%)"]
                    if focus_areas:
                        for idx, m in enumerate(focus_areas, 1):
                            perf_pct = m.get('performance_percentage', 0) or 0
                            right_content.append(f"{idx}. {m.get('measure', 'Unknown')} - {perf_pct:.1f}%")
                    else:
                        right_content.append("No focus areas - all measures at or above 75%!")

                    # Build two-column layout
                    left_text = "\n".join(left_content)
                    right_text = "\n".join(right_content)

                    two_col_table = Table([
                        [Paragraph(left_text.replace("\n", "<br/>"), styles['Normal']),
                         Paragraph(right_text.replace("\n", "<br/>"), styles['Normal'])]
                    ], colWidths=[3.25*inch, 3.25*inch])
                    two_col_table.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9f9f9')),
                    ]))
                    story.append(two_col_table)
                    story.append(Spacer(1, 0.2*inch))
                except Exception as e:
                    logger.error(f"Error creating strengths/focus areas: {str(e)}", exc_info=True)

            # Recommended Next Steps
            story.append(Paragraph("RECOMMENDED NEXT STEPS", heading_style))
            story.append(Paragraph(next_steps, styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
            story.append(Paragraph(f"<i>Report Period: All observations</i>", ParagraphStyle('Italic', parent=styles['Normal'], fontSize=9, textColor=colors.grey)))

            # Build PDF
            doc.build(story)
            pdf_buffer.seek(0)

            pdf_data = pdf_buffer.getvalue()
            # Write to temp file for FileResponse
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(pdf_data)
                tmp_path = tmp.name

            # Use student name in filename, sanitize it
            safe_name = student.name.replace(" ", "_").replace("/", "_")
            return FileResponse(
                tmp_path,
                media_type="application/pdf",
                filename=f"student_report_{safe_name}.pdf"
            )

        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

@router.get("/class/{class_code}")
async def generate_class_report(
    class_code: str,
    format: str = Query("pdf", regex="^(pdf|html)$"),
    session: AsyncSession = Depends(get_session)
):
    """Generate class report (PDF or HTML)."""
    # Verify class exists
    class_query = select(Class).where(Class.class_code == class_code)
    class_result = await session.execute(class_query)
    class_obj = class_result.scalar_one_or_none()

    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    if format == "html":
        # Return JSON representation
        student_query = select(Student).where(Student.primary_class == class_code)
        student_result = await session.execute(student_query)
        students = student_result.scalars().all()

        student_data = []
        for student in students:
            perf, _, _, _, _ = await CalculationService.calculate_performance(
                session, student_id=student.student_id
            )
            attendance = await CalculationService.calculate_attendance_rate(
                session, student_id=student.student_id
            )
            band_name, _ = CalculationService.get_performance_band(perf)

            student_data.append({
                "student_id": student.student_id,
                "name": student.name,
                "achievement": CalculationService.format_percentage(perf),
                "attendance": CalculationService.format_percentage(attendance),
                "band": band_name
            })

        return {
            "class_code": class_code,
            "class_name": class_obj.class_name,
            "generated_at": datetime.now().isoformat(),
            "total_students": len(students),
            "students": student_data
        }

    else:  # PDF
        try:
            # Get all students in class
            student_query = select(Student).where(Student.primary_class == class_code)
            student_result = await session.execute(student_query)
            students = student_result.scalars().all()

            if not students:
                # Create a simple PDF indicating no students in class
                pdf_buffer = BytesIO()
                doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

                styles = getSampleStyleSheet()
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=20,
                    textColor=colors.black,
                    spaceAfter=20,
                    alignment=1
                )

                story = []
                story.append(Paragraph("CLASS ENGAGEMENT REPORT", title_style))
                story.append(Spacer(1, 0.2*inch))
                story.append(Paragraph(f"<b>Class:</b> {class_obj.class_name} ({class_code})", styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
                story.append(Paragraph("No students found in this class.", styles['Normal']))

                doc.build(story)
                pdf_buffer.seek(0)

                pdf_data = pdf_buffer.getvalue()
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    tmp.write(pdf_data)
                    tmp_path = tmp.name

                safe_name = class_obj.class_name.replace(" ", "_").replace("/", "_")
                return FileResponse(
                    tmp_path,
                    media_type="application/pdf",
                    filename=f"class_report_{safe_name}.pdf"
                )

            # Create PDF in memory
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=colors.black,
                spaceAfter=12,
                alignment=1  # Center
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=colors.black,
                spaceAfter=10,
                fontName='Helvetica-Bold'
            )

            story = []

            # Title
            story.append(Paragraph("CLASS ENGAGEMENT REPORT", title_style))
            story.append(Spacer(1, 0.15*inch))

            # Header info table
            header_data = [
                ["Class Name:", class_obj.class_name, "Class Code:", class_code],
                ["Report Date:", datetime.now().strftime('%Y-%m-%d'), "", ""]
            ]
            header_table = Table(header_data, colWidths=[1.2*inch, 2*inch, 1.2*inch, 2*inch])
            header_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            story.append(header_table)
            story.append(Spacer(1, 0.2*inch))

            # Class Statistics Summary
            story.append(Paragraph("CLASS STATISTICS SUMMARY", heading_style))

            total_students = len(students)
            students_with_data = 0
            class_avg_perf = 0
            class_avg_attendance = 0

            student_summaries = []
            for student in students:
                perf, _, _, _, _ = await CalculationService.calculate_performance(
                    session, student_id=student.student_id
                )
                attendance = await CalculationService.calculate_attendance_rate(
                    session, student_id=student.student_id
                )

                if perf is not None:
                    band_name, _ = CalculationService.get_performance_band(perf)
                    students_with_data += 1
                    class_avg_perf += perf
                    class_avg_attendance += attendance
                else:
                    band_name = "N/A"

                student_summaries.append({
                    'name': student.name,
                    'student_id': student.student_id,
                    'performance': perf if perf is not None else 0,
                    'attendance': attendance if attendance is not None else 0,
                    'band': band_name
                })

            if students_with_data > 0:
                class_avg_perf /= students_with_data
                class_avg_attendance /= students_with_data

            if students_with_data == 0:
                # No observation data message
                story.append(Paragraph(
                    "<b>⚠️ Note:</b> No observation data available for any students in this class.",
                    ParagraphStyle('Warning', parent=styles['Normal'], textColor=colors.HexColor('#B8860B'), fontSize=11)
                ))
                story.append(Spacer(1, 0.2*inch))

            stats_data = [
                ["Total Students:", str(total_students), "Students with Data:", str(students_with_data)],
                ["Class Average Achievement:", CalculationService.format_percentage(class_avg_perf) if students_with_data > 0 else "N/A", "Class Average Attendance:", CalculationService.format_percentage(class_avg_attendance) if students_with_data > 0 else "N/A"]
            ]
            stats_table = Table(stats_data, colWidths=[1.8*inch, 1.2*inch, 1.8*inch, 1.2*inch])
            stats_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
            ]))
            story.append(stats_table)
            story.append(Spacer(1, 0.2*inch))

            # Performance Distribution Visualization
            if students_with_data > 0:
                story.append(Paragraph("PERFORMANCE DISTRIBUTION", heading_style))

                # Calculate performance band distribution
                band_counts = {}
                for student in student_summaries:
                    band = student['band']
                    band_counts[band] = band_counts.get(band, 0) + 1

                # Create pie chart
                try:
                    pie_data = [(count, band) for band, count in sorted(band_counts.items(), key=lambda x: x[1], reverse=True)]

                    if pie_data:
                        drawing = Drawing(3*inch, 1.8*inch)
                        pie = Pie()
                        pie.data = [count for count, _ in pie_data]
                        pie.labels = [f"{band}\n({count})" for count, band in pie_data]
                        pie.width = 2.5*inch
                        pie.height = 1.5*inch
                        pie.x = 0.2*inch
                        pie.y = 0.1*inch

                        # Color map for bands
                        band_colors = {
                            'Exemplary': colors.HexColor('#059669'),
                            'Proficient': colors.HexColor('#0369a1'),
                            'Developing': colors.HexColor('#ca8a04'),
                            'Emerging': colors.HexColor('#ea580c'),
                            'Beginning': colors.HexColor('#dc2626'),
                            'Needs Intensive Support': colors.HexColor('#7f1d1d'),
                        }

                        pie.slices.strokeWidth = 1
                        pie.slices.strokeColor = colors.white
                        for idx, (_, band) in enumerate(pie_data):
                            pie.slices[idx].fillColor = band_colors.get(band, colors.grey)

                        drawing.add(pie)
                        story.append(drawing)
                        story.append(Spacer(1, 0.1*inch))
                except Exception as e:
                    logger.error(f"Error creating pie chart: {str(e)}", exc_info=True)
                    story.append(Paragraph(f"<i>Could not display chart: {str(e)}</i>", styles['Normal']))

                story.append(Spacer(1, 0.2*inch))

                # Performance Level Breakdown
                story.append(Paragraph("ACHIEVEMENT LEVEL BREAKDOWN", heading_style))

                try:
                    # Sort students by achievement and count in ranges
                    perf_ranges = {
                        '90-100%': 0,
                        '80-89%': 0,
                        '70-79%': 0,
                        '60-69%': 0,
                        '50-59%': 0,
                        '<50%': 0,
                        'No Data': 0
                    }

                    for student in student_summaries:
                        perf = student['performance']
                        if perf == 0 and student['band'] == 'N/A':
                            perf_ranges['No Data'] += 1
                        elif perf >= 90:
                            perf_ranges['90-100%'] += 1
                        elif perf >= 80:
                            perf_ranges['80-89%'] += 1
                        elif perf >= 70:
                            perf_ranges['70-79%'] += 1
                        elif perf >= 60:
                            perf_ranges['60-69%'] += 1
                        elif perf >= 50:
                            perf_ranges['50-59%'] += 1
                        else:
                            perf_ranges['<50%'] += 1

                    # Create bar chart
                    breakdown_drawing = Drawing(6.5*inch, 2*inch)
                    chart = VerticalBarChart()

                    # Prepare data: only include non-zero categories
                    categories = [k for k, v in perf_ranges.items() if v > 0 or k == '90-100%']
                    chart_data = [[perf_ranges.get(cat, 0) for cat in categories]]

                    chart.data = chart_data
                    chart.categoryAxis.categoryNames = categories
                    chart.categoryAxis.labels.angle = 45
                    chart.valueAxis.valueMax = max(chart_data[0]) if chart_data[0] else 1
                    chart.width = 5.5*inch
                    chart.height = 1.8*inch
                    chart.x = 0.5*inch
                    chart.y = 0.1*inch

                    # Set bar color
                    chart.bars[0].fillColor = colors.HexColor('#3b82f6')

                    breakdown_drawing.add(chart)
                    story.append(breakdown_drawing)
                    story.append(Spacer(1, 0.2*inch))
                except Exception as e:
                    logger.error(f"Error creating bar chart: {str(e)}", exc_info=True)
                    story.append(Paragraph(f"<i>Could not display breakdown chart</i>", styles['Normal']))
                    story.append(Spacer(1, 0.2*inch))

            # Page break before student rankings
            story.append(PageBreak())

            # Repeat class header on second page
            story.append(Paragraph("CLASS ENGAGEMENT REPORT", title_style))
            story.append(Spacer(1, 0.15*inch))

            header_data_page2 = [
                ["Class Name:", class_obj.class_name, "Class Code:", class_code],
                ["Report Date:", datetime.now().strftime('%Y-%m-%d'), "", ""]
            ]
            header_table_page2 = Table(header_data_page2, colWidths=[1.2*inch, 2*inch, 1.2*inch, 2*inch])
            header_table_page2.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            story.append(header_table_page2)
            story.append(Spacer(1, 0.2*inch))

            # Student rankings
            story.append(Paragraph("STUDENT PERFORMANCE RANKINGS", heading_style))

            if not student_summaries:
                story.append(Paragraph(
                    "<i>No students in class.</i>",
                    styles['Normal']
                ))
            else:
                # Sort by performance descending
                sorted_students = sorted(student_summaries, key=lambda x: x['performance'], reverse=True)

                student_data = [[
                    Paragraph("<b>Rank</b>", styles['Normal']),
                    Paragraph("<b>Student Name</b>", styles['Normal']),
                    Paragraph("<b>Achievement %</b>", styles['Normal']),
                    Paragraph("<b>Attendance %</b>", styles['Normal']),
                    Paragraph("<b>Band</b>", styles['Normal'])
                ]]

                for idx, student in enumerate(sorted_students, 1):
                    student_data.append([
                        Paragraph(str(idx), styles['Normal']),
                        Paragraph(student['name'], styles['Normal']),
                        Paragraph(CalculationService.format_percentage(student['performance']) if student['performance'] > 0 else "N/A", styles['Normal']),
                        Paragraph(CalculationService.format_percentage(student['attendance']) if student['attendance'] > 0 else "N/A", styles['Normal']),
                        Paragraph(student['band'], styles['Normal'])
                    ])

                student_table = Table(student_data, colWidths=[0.6*inch, 2.2*inch, 1.2*inch, 1.2*inch, 1.4*inch])
                student_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#808080')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('TOPPADDING', (0, 0), (-1, 0), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
                ]))
                story.append(student_table)

            # Build PDF
            doc.build(story)
            pdf_buffer.seek(0)

            pdf_data = pdf_buffer.getvalue()
            # Write to temp file for FileResponse
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(pdf_data)
                tmp_path = tmp.name

            # Use class name in filename, sanitize it
            safe_name = class_obj.class_name.replace(" ", "_").replace("/", "_")
            return FileResponse(
                tmp_path,
                media_type="application/pdf",
                filename=f"class_report_{safe_name}.pdf"
            )

        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
