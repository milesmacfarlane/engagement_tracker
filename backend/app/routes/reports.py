"""Report generation routes."""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
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
                fontSize=24,
                textColor=colors.HexColor('#1F4788'),
                spaceAfter=30,
                alignment=1  # Center
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#1F4788'),
                spaceAfter=12
            )

            story = []

            # Title
            story.append(Paragraph("Student Engagement Report", title_style))
            story.append(Spacer(1, 0.2*inch))

            # Student info
            info_data = [
                ["Student Name:", student.name],
                ["Student ID:", student.student_id],
                ["Class:", student.primary_class],
                ["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M")]
            ]
            info_table = Table(info_data, colWidths=[2*inch, 3.5*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            story.append(info_table)
            story.append(Spacer(1, 0.3*inch))

            # Overall performance with color-coded boxes
            story.append(Paragraph("Overall Performance", heading_style))

            # Create 4 metrics boxes
            metrics_data = [
                [
                    f"<b>Achievement %</b><br/><font size=18><b>{CalculationService.format_percentage(overall_perf)}</b></font>",
                    f"<b>Performance Band</b><br/><font size=14><b>{band_name}</b></font>",
                    f"<b>Attendance %</b><br/><font size=18><b>{CalculationService.format_percentage(attendance)}</b></font>",
                    f"<b>Days Observed</b><br/><font size=14><b>{days_observed}</b></font>"
                ]
            ]
            metrics_table = Table(metrics_data, colWidths=[1.4*inch, 1.4*inch, 1.4*inch, 1.4*inch])

            # Color the boxes based on achievement
            if overall_perf and overall_perf >= 80:
                box_color = colors.HexColor('#dcfce7')  # Green
            elif overall_perf and overall_perf >= 60:
                box_color = colors.HexColor('#dbeafe')  # Blue
            else:
                box_color = colors.HexColor('#fef3c7')  # Yellow

            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), box_color),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#1F4788')),
                ('LINEWIDTH', (0, 0), (-1, -1), 2),
            ]))
            story.append(metrics_table)
            story.append(Spacer(1, 0.3*inch))

            # Measure breakdown with visual chart
            story.append(Paragraph("Performance by Measure", heading_style))

            if not has_data or not measure_breakdown:
                story.append(Paragraph(
                    "<i>No observation data available. No performance measurements to display.</i>",
                    styles['Normal']
                ))
            else:
                try:
                    # Create measure chart with color-coded performance bars
                    measure_data = [["Measure", "Performance", "Band"]]

                    for m in measure_breakdown:
                        perf_pct = m.get('performance_percentage', 0) or 0
                        band = m.get('band', 'N/A')

                        # Create a visual bar using simple characters
                        bar_width = int(perf_pct / 5)  # 20 chars = 100%
                        bar_text = "#" * bar_width + "-" * (20 - bar_width)

                        measure_data.append([
                            m.get('measure', 'Unknown')[:20],
                            f"{bar_text} {CalculationService.format_percentage(perf_pct)}",
                            band
                        ])

                    measure_table = Table(measure_data, colWidths=[2.0*inch, 2.5*inch, 1.5*inch])

                    # Color rows based on performance band
                    style_list = [
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4788')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTNAME', (2, 1), (2, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('LEFTPADDING', (0, 0), (-1, -1), 6),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
                        ('LINEWIDTH', (0, 0), (-1, 0), 1.5),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
                    ]

                    # Add row colors based on band
                    for idx, m in enumerate(measure_breakdown, 1):
                        band = m.get('band', 'N/A')
                        if band == 'Exemplary':
                            color = colors.HexColor('#dcfce7')  # Light green
                        elif band == 'Proficient':
                            color = colors.HexColor('#dbeafe')  # Light blue
                        elif band == 'Developing':
                            color = colors.HexColor('#fef3c7')  # Light yellow
                        elif band == 'Emerging':
                            color = colors.HexColor('#fed7aa')  # Light orange
                        else:
                            color = colors.HexColor('#fecaca')  # Light red

                        # Override the background for this row with the band color
                        style_list.append(('BACKGROUND', (0, idx), (-1, idx), color))

                    measure_table.setStyle(TableStyle(style_list))
                    story.append(measure_table)
                except Exception as e:
                    logger.error(f"Error creating measure table: {str(e)}", exc_info=True)
                    story.append(Paragraph(
                        f"<i>Could not display measure breakdown: {str(e)}</i>",
                        styles['Normal']
                    ))
            story.append(Spacer(1, 0.3*inch))

            # Next steps
            story.append(Paragraph("Recommended Next Steps", heading_style))
            story.append(Paragraph(next_steps, styles['Normal']))

            # Build PDF
            doc.build(story)
            pdf_buffer.seek(0)

            pdf_data = pdf_buffer.getvalue()
            # Write to temp file for FileResponse
            import tempfile
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
                    fontSize=24,
                    textColor=colors.HexColor('#1F4788'),
                    spaceAfter=30,
                    alignment=1
                )

                story = []
                story.append(Paragraph("Class Engagement Report", title_style))
                story.append(Spacer(1, 0.2*inch))
                story.append(Paragraph(f"Class: {class_obj.class_name} ({class_code})", styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
                story.append(Paragraph("No students found in this class.", styles['Normal']))

                doc.build(story)
                pdf_buffer.seek(0)

                pdf_data = pdf_buffer.getvalue()
                return StreamingResponse(
                    BytesIO(pdf_data),
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f"attachment; filename=class_report_{class_code}.pdf",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization",
                    }
                )

            # Create PDF in memory
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1F4788'),
                spaceAfter=30,
                alignment=1  # Center
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#1F4788'),
                spaceAfter=12
            )

            story = []

            # Title
            story.append(Paragraph("Class Engagement Report", title_style))
            story.append(Spacer(1, 0.2*inch))

            # Class info
            info_data = [
                ["Class Name:", class_obj.class_name],
                ["Class Code:", class_code],
                ["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M")]
            ]
            info_table = Table(info_data, colWidths=[2*inch, 3.5*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            story.append(info_table)
            story.append(Spacer(1, 0.3*inch))

            # Class statistics
            story.append(Paragraph("Class Statistics", heading_style))

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
                ["Total Students:", str(total_students)],
                ["Students with Data:", str(students_with_data)],
                ["Class Average Achievement:", CalculationService.format_percentage(class_avg_perf) if students_with_data > 0 else "N/A"],
                ["Class Average Attendance:", CalculationService.format_percentage(class_avg_attendance) if students_with_data > 0 else "N/A"]
            ]
            stats_table = Table(stats_data, colWidths=[2*inch, 3.5*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            story.append(stats_table)
            story.append(Spacer(1, 0.3*inch))

            # Student rankings
            story.append(Paragraph("Student Performance Rankings", heading_style))

            if not student_summaries:
                story.append(Paragraph(
                    "<i>No students in class.</i>",
                    styles['Normal']
                ))
            else:
                # Sort by performance descending
                sorted_students = sorted(student_summaries, key=lambda x: x['performance'], reverse=True)

                student_data = [["Rank", "Student Name", "Achievement %", "Attendance %", "Band"]]
                for idx, student in enumerate(sorted_students, 1):
                    student_data.append([
                        str(idx),
                        student['name'][:20],
                        CalculationService.format_percentage(student['performance']) if student['performance'] > 0 else "N/A",
                        CalculationService.format_percentage(student['attendance']) if student['attendance'] > 0 else "N/A",
                        student['band']
                    ])

                student_table = Table(student_data, colWidths=[0.6*inch, 2.2*inch, 1.2*inch, 1.2*inch, 1.4*inch])
                student_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4788')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
                ]))
                story.append(student_table)

            # Build PDF
            doc.build(story)
            pdf_buffer.seek(0)

            pdf_data = pdf_buffer.getvalue()
            # Use class name in filename, sanitize it
            safe_name = class_obj.class_name.replace(" ", "_").replace("/", "_")
            return StreamingResponse(
                BytesIO(pdf_data),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=class_report_{safe_name}.pdf",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization",
                }
            )

        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
