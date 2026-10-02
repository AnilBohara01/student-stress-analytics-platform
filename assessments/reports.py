import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from .feedback import generate_personalized_feedback


def generate_assessment_pdf(assessment) -> io.BytesIO:
    """
    Generates a publication-quality PDF report for a student stress assessment.

    Parameters:
        assessment (Assessment): Assessment model instance.

    Returns:
        io.BytesIO: Buffer containing generated PDF byte data.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom Colors
    PRIMARY = colors.HexColor("#4f46e5")
    SECONDARY = colors.HexColor("#7c3aed")
    DARK_BG = colors.HexColor("#0f172a")
    TEXT_MAIN = colors.HexColor("#1e293b")
    TEXT_MUTED = colors.HexColor("#64748b")
    STRESS_HIGH = colors.HexColor("#e11d48")
    STRESS_LOW = colors.HexColor("#059669")
    LIGHT_BG = colors.HexColor("#f8fafc")

    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY,
        alignment=TA_LEFT
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=TEXT_MUTED,
        alignment=TA_LEFT
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=PRIMARY,
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=TEXT_MAIN
    )

    disclaimer_style = ParagraphStyle(
        'DisclaimerText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#991b1b")
    )

    story = []

    # 1. Header Title & Subtitle
    story.append(Paragraph("StressLens — Student Assessment & Lifestyle Report", title_style))
    story.append(Paragraph("Explainable AI Stress Assessment & Lifestyle Analytics Platform", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceBefore=0, spaceAfter=12))

    # 2. Metadata Grid
    meta_data = [
        [
            Paragraph(f"<b>Student:</b> {assessment.user.username}", body_style),
            Paragraph(f"<b>Report ID:</b> #{assessment.pk}", body_style)
        ],
        [
            Paragraph(f"<b>Assessment Date:</b> {assessment.created_at.strftime('%B %d, %Y - %H:%M')}", body_style),
            Paragraph(f"<b>Model Version:</b> {assessment.model_version}", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # 3. Prediction Result Banner
    is_high = (assessment.predicted_stress_level == 1)
    status_text = "HIGH STRESS DETECTED" if is_high else "LOW / NORMAL STRESS"
    status_color = STRESS_HIGH if is_high else STRESS_LOW

    prob_low_pct = f"{assessment.probability_low_stress * 100:.1f}%"
    prob_high_pct = f"{assessment.probability_high_stress * 100:.1f}%"

    pred_data = [
        [
            Paragraph(f"<font color='{status_color.hexval()}'><b>PREDICTED RESULT: {status_text}</b></font>", ParagraphStyle('ResultBanner', fontName='Helvetica-Bold', fontSize=13, leading=16)),
            Paragraph(f"<b>High Stress Prob:</b> {prob_high_pct}<br/><b>Low Stress Prob:</b> {prob_low_pct}", body_style)
        ]
    ]
    pred_table = Table(pred_data, colWidths=[320, 220])
    pred_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('LINELEFT', (0, 0), (0, 0), 4, status_color),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(pred_table)
    story.append(Spacer(1, 12))

    # 4. SHAP Feature Attribution
    story.append(Paragraph("1. SHAP AI Feature Attribution", section_heading))
    story.append(Paragraph(f"<b>AI Summary Narrative:</b> {assessment.narrative_explanation}", body_style))
    story.append(Spacer(1, 6))

    shap_rows = [["Feature Name", "SHAP Impact Value", "Impact Direction"]]
    for factor in assessment.top_contributing_factors[:5]:
        direction_text = "Increases Stress Score" if factor['shap_value'] > 0 else "Supports Stress Reduction"
        shap_rows.append([
            factor['feature_label'],
            f"{factor['shap_value']:+.4f}",
            direction_text
        ])

    shap_table = Table(shap_rows, colWidths=[200, 140, 200])
    shap_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ]))
    story.append(shap_table)
    story.append(Spacer(1, 12))

    # 5. Recorded Lifestyle Indicators Summary Table
    story.append(Paragraph("2. Recorded Lifestyle Indicators", section_heading))
    input_rows = [
        ["Indicator Name", "Recorded Value", "Indicator Name", "Recorded Value"],
        ["Student Category", assessment.get_student_type_display(), "Attendance Rate", f"{assessment.attendance}%"],
        ["Sleep Duration", f"{assessment.sleep_hours} Hours", "Exam Pressure", f"{assessment.exam_pressure} / 10"],
        ["Study Duration", f"{assessment.study_hours} Hours", "Family Support", f"{assessment.family_support} / 10"],
        ["Social Media Screen Time", f"{assessment.social_media_hours} Hours", "Academic Month", f"Month {assessment.month}"]
    ]
    input_table = Table(input_rows, colWidths=[140, 130, 140, 130])
    input_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#334155")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ]))
    story.append(input_table)
    story.append(Spacer(1, 12))

    # 6. Personalized Non-Clinical Feedback
    story.append(Paragraph("3. Actionable Non-Clinical Guidance", section_heading))
    input_dict = {
        'Sleep_Hours': assessment.sleep_hours,
        'Study_Hours': assessment.study_hours,
        'Social_Media_Hours': assessment.social_media_hours,
        'Attendance': assessment.attendance,
        'Exam_Pressure': assessment.exam_pressure,
        'Family_Support': assessment.family_support
    }
    feedback_cards = generate_personalized_feedback(input_dict, assessment.predicted_stress_level)

    for item in feedback_cards[:4]:
        feedback_p = Paragraph(f"<b>[{item['category']}] {item['title']}:</b> {item['suggestion']}", body_style)
        fb_table = Table([[feedback_p]], colWidths=[540])
        fb_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('LINELEFT', (0, 0), (0, 0), 3, PRIMARY),
        ]))
        story.append(fb_table)
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 8))

    # 7. Non-Clinical Educational Disclaimer Box
    disc_text = (
        "<b>Educational & Research Disclaimer:</b> This report is generated by StressLens for educational and "
        "lifestyle analytics purposes. It uses machine learning models to assess student stress indicators. "
        "This report does NOT constitute a medical or psychological diagnosis. If experiencing severe stress, "
        "please consult a certified healthcare professional or campus student counselor."
    )
    disc_table = Table([[Paragraph(disc_text, disclaimer_style)]], colWidths=[540])
    disc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fef2f2")),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#fca5a5")),
    ]))
    story.append(disc_table)

    doc.build(story)
    buffer.seek(0)
    return buffer
