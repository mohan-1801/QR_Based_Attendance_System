from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_attendance_pdf(title, subtitle, records, metadata=None):
    """
    Generates a PDF document for attendance records using ReportLab.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=15
    )

    elements = []
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph(subtitle, subtitle_style))

    if metadata:
        meta_data = [[f"<b>{k}:</b>", str(v)] for k, v in metadata.items()]
        meta_table = Table(meta_data, colWidths=[120, 380])
        meta_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#334155')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (9, 9), (-1, -1)),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 15))

    # Table Header
    table_data = [["#", "Roll No", "Student Name", "Subject", "Date & Time", "Status", "Method"]]
    
    for idx, r in enumerate(records, 1):
        status_color = "#16a34a" if r.status == "PRESENT" else "#d97706" if r.status == "LATE" else "#dc2626"
        table_data.append([
            str(idx),
            r.student.roll_number,
            r.student.user.get_full_name_or_username(),
            r.subject.code,
            r.marked_at.strftime("%Y-%m-%d %H:%M"),
            r.get_status_display(),
            r.get_verification_method_display()
        ])

    col_widths = [25, 75, 130, 80, 100, 55, 60]
    t = Table(table_data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8.5),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(t)
    doc.build(elements)

    buffer.seek(0)
    return buffer.getvalue()
