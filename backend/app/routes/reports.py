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
            band_name, _ = CalculationService.get_performance_band(overall_perf)
            next_steps = CalculationService.get_recommended_next_steps(overall_perf)

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

            # Overall performance
            story.append(Paragraph("Overall Performance", heading_style))
            perf_data = [
                ["Overall Achievement %:", CalculationService.format_percentage(overall_perf)],
                ["Performance Band:", band_name],
                ["Attendance Rate:", CalculationService.format_percentage(attendance)],
                ["Days Observed:", str(days_observed)]
            ]
            perf_table = Table(perf_data, colWidths=[2*inch, 3.5*inch])
            perf_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            story.append(perf_table)
            story.append(Spacer(1, 0.3*inch))

            # Measure breakdown
            story.append(Paragraph("Measure Breakdown", heading_style))
            measure_data = [["Measure", "Performance %", "Band", "Status"]]
            for m in measure_breakdown:
                measure_data.append([
                    m['measure'][:25],
                    CalculationService.format_percentage(m['performance_percentage']),
                    m['band'],
                    m['status']
                ])

            measure_table = Table(measure_data, colWidths=[2.5*inch, 1.5*inch, 1.2*inch, 0.8*inch])
            measure_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
            ]))
            story.append(measure_table)
            story.append(Spacer(1, 0.3*inch))

            # Next steps
            story.append(Paragraph("Recommended Next Steps", heading_style))
            story.append(Paragraph(next_steps, styles['Normal']))

            # Build PDF
            doc.build(story)
            pdf_buffer.seek(0)

            return FileResponse(
                BytesIO(pdf_buffer.getvalue()),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=student_report_{student_id}.pdf"}
            )

        except Exception as e:
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
        return {"message": "PDF generation coming soon"}
