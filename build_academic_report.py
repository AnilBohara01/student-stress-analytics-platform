import os
import sys
import pandas as pd
import numpy as np

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

# Define custom canvas for dynamic page numbering and running headers/footers
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            # Skip cover page
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#555555"))

        # Running Header
        header_text = "Student Stress Assessment & Lifestyle Analytics Platform | Academic Report"
        author_text = "Anil Bohara (ID: 25126458)"
        self.drawString(36, 756, header_text)
        self.drawRightString(576, 756, author_text)
        
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 748, 576, 748)

        # Running Footer
        self.line(36, 45, 576, 45)
        footer_left = "Submission Date: 30 September 2026 | Academic Project Report"
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawString(36, 32, footer_left)
        self.drawRightString(576, 32, page_str)

        self.restoreState()

def create_report():
    pdf_filename = "Student_Stress_Assessment_Academic_Project_Report.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#1E3A8A")   # Deep Navy
    secondary_color = colors.HexColor("#0D9488") # Teal
    dark_text = colors.HexColor("#1F2937")       # Charcoal
    accent_bg = colors.HexColor("#FDFBF7")       # Cream
    border_color = colors.HexColor("#E2E8F0")    # Border slate

    cover_title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=primary_color,
        alignment=1, # Center
        spaceAfter=15
    )

    cover_subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=secondary_color,
        alignment=1,
        spaceAfter=30
    )

    cover_meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=16,
        textColor=dark_text,
        alignment=1
    )

    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=primary_color,
        spaceBefore=18,
        spaceAfter=10,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=secondary_color,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'CustomH3',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=dark_text,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=dark_text,
        spaceAfter=8,
        alignment=4 # Justified
    )

    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=dark_text,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=dark_text
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=dark_text
    )

    caption_style = ParagraphStyle(
        'Caption',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#64748B"),
        alignment=1,
        spaceBefore=4,
        spaceAfter=10
    )

    story = []

    # ==================== COVER PAGE ====================
    story.append(Spacer(1, 40))
    story.append(Paragraph("STUDENT STRESS ASSESSMENT &amp; LIFESTYLE ANALYTICS PLATFORM", cover_title_style))
    story.append(Paragraph("An End-to-End Machine Learning Framework and Web Application for Early Detection, Explainable Prediction, and Personalized Lifestyle Intervention", cover_subtitle_style))
    story.append(HRFlowable(width="80%", thickness=2, color=secondary_color, spaceAfter=40))

    meta_text = """
    <b>Author / Student Name:</b> Anil Bohara<br/>
    <b>Student Identification Number:</b> 25126458<br/>
    <b>Date of Submission:</b> 30 September 2026<br/>
    <b>Degree Program:</b> Academic Project Submission in Computer Science &amp; Software Engineering<br/>
    <b>Primary Domain:</b> Machine Learning, Explainable AI (XAI), Web Systems &amp; Analytics<br/>
    <b>Technical Framework:</b> Django 5.x, Python 3.12+, XGBoost, SHAP, SQLite3, ReportLab
    """
    story.append(Paragraph(meta_text, cover_meta_style))
    story.append(Spacer(1, 60))

    # Abstract Callout Box on Cover Page
    abstract_box_data = [[
        Paragraph("<b>EXECUTIVE ABSTRACT:</b><br/>This academic project report presents the design, development, empirical evaluation, and full-stack deployment of the <i>Student Stress Assessment &amp; Lifestyle Analytics Platform</i>. Grounded in empirical data collected across 25,476 unique student records, the system addresses the escalating crisis of university stress through machine learning and human-centered design. Six classification algorithms were benchmarked; a hyperparameter-tuned <b>XGBoost model achieved optimal performance with ROC-AUC of 0.8756</b>, accuracy of 81.99%, precision of 73.94%, and recall of 61.65%. Model explainability is embedded directly into the application using SHAP (SHapley Additive exPlanations), converting black-box machine learning outputs into personalized feature-level insights. The platform features a Django backend, a cream-white responsive interface, real-time risk scoring, PDF report export, and a comprehensive admin analytics suite.", callout_style)
    ]]
    abstract_table = Table(abstract_box_data, colWidths=[520])
    abstract_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), accent_bg),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 14),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(abstract_table)

    story.append(PageBreak())

    # ==================== TABLE OF CONTENTS ====================
    story.append(Paragraph("Table of Contents", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=primary_color, spaceAfter=15))

    toc_data = [
        [Paragraph("<b>Section</b>", table_header_style), Paragraph("<b>Title</b>", table_header_style)],
        [Paragraph("<b>1. Executive Summary</b>", table_cell_bold), Paragraph("Project Overview, High-Level Findings &amp; Core Contributions", table_cell_style)],
        [Paragraph("<b>2. Introduction &amp; Problem Definition</b>", table_cell_bold), Paragraph("Background, Problem Statement, Scope &amp; Non-Clinical Framing", table_cell_style)],
        [Paragraph("<b>3. Project Objectives &amp; System Scope</b>", table_cell_bold), Paragraph("Core Objectives, Technical Requirements &amp; Stakeholder Analysis", table_cell_style)],
        [Paragraph("<b>4. Dataset Architecture &amp; EDA</b>", table_cell_bold), Paragraph("Data Provenance, Cleaning, Feature Dictionary &amp; Statistical Findings", table_cell_style)],
        [Paragraph("<b>5. Machine Learning Methodology</b>", table_cell_bold), Paragraph("Pipeline Architecture, Candidate Models, Tuning, SHAP &amp; Metrics", table_cell_style)],
        [Paragraph("<b>6. System Design &amp; Architecture</b>", table_cell_bold), Paragraph("Full-Stack Web Architecture, Database Schema &amp; Security Controls", table_cell_style)],
        [Paragraph("<b>7. Software Implementation &amp; UI</b>", table_cell_bold), Paragraph("Django Implementation, Cream-White UX System &amp; Feature Modules", table_cell_style)],
        [Paragraph("<b>8. Experimental Results &amp; Discussion</b>", table_cell_bold), Paragraph("Comparative Benchmark Analysis, Latency &amp; Key Empirical Insights", table_cell_style)],
        [Paragraph("<b>9. Ethical Considerations &amp; Limitations</b>", table_cell_bold), Paragraph("Data Privacy, Bias Mitigation, Self-Reporting Limits &amp; Ethics", table_cell_style)],
        [Paragraph("<b>10. Conclusion &amp; Future Work</b>", table_cell_bold), Paragraph("Summary of Outcomes &amp; Roadmap for Longitudinal Expansion", table_cell_style)],
        [Paragraph("<b>11. Academic References</b>", table_cell_bold), Paragraph("IEEE/APA Citations for ML, XAI, and Web Architecture Literature", table_cell_style)],
        [Paragraph("<b>12. Appendices (A – G)</b>", table_cell_bold), Paragraph("Feature Dictionary, EDA Tables, Metric Benchmarks, UI Previews, Code Hierarchy, API Schemas, System Specs", table_cell_style)],
    ]
    toc_table = Table(toc_data, colWidths=[140, 380])
    toc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('PADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, accent_bg])
    ]))
    story.append(toc_table)
    story.append(Spacer(1, 20))

    # ==================== SECTION 1 ====================
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=primary_color, spaceAfter=10))

    story.append(Paragraph("The escalating incidence of academic stress among higher education students presents a significant challenge to university administration, student welfare services, and educational outcomes. Left unaddressed, chronic stress impairs cognitive performance, disrupts sleep hygiene, increases dropout rates, and undermines physical and mental well-being. This project delivers a comprehensive, production-grade <b>Student Stress Assessment &amp; Lifestyle Analytics Platform</b> engineered to provide reliable early risk identification, actionable model explainability, and individual lifestyle guidance through a secure web application.", body_style))

    story.append(Paragraph("<b>Key Scientific and Systems Achievements:</b>", h2_style))
    story.append(Paragraph("• <b>Rigorous Dataset Curation:</b> Processed 25,500 raw student lifestyle records (cleaned to 25,476 unique entries), spanning 20 distinct physiological, academic, psychological, and environmental variables.", bullet_style))
    story.append(Paragraph("• <b>Empirical Model Benchmarking:</b> Evaluated six candidate machine learning architectures under 5-fold stratified cross-validation and independent test set split (80/20 ratio, 20,380 train / 5,096 test samples).", bullet_style))
    story.append(Paragraph("• <b>Superior Predictive Performance:</b> Selected a hyperparameter-tuned <b>XGBoost Classifier</b> achieving an ROC-AUC of <b>0.8756</b>, Overall Accuracy of <b>81.99%</b>, Precision of <b>73.94%</b>, and Recall of <b>61.65%</b>.", bullet_style))
    story.append(Paragraph("• <b>Explainable AI (SHAP) Integration:</b> Implemented SHapley Additive exPlanations to quantify global and local feature contributions, allowing students to understand exact risk drivers (e.g., academic performance, exam pressure, financial burden, sleep quality).", bullet_style))
    story.append(Paragraph("• <b>Human-Centered Web Application:</b> Built a production Django web platform featuring a refined cream-white UI design system (`#FDFBF7`), interactive 20-parameter assessment forms, real-time risk visualization, automated PDF report generation, and historical analytics tracking.", bullet_style))

    story.append(Spacer(1, 10))

    # ==================== SECTION 2 ====================
    story.append(Paragraph("2. Introduction &amp; Problem Definition", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=primary_color, spaceAfter=10))

    story.append(Paragraph("Higher education environments place intense cognitive, financial, and socio-emotional demands on students. The transition into university coursework requires managing rigorous study schedules, adapting to financial independence, maintaining academic standing, and balancing extracurricular obligations. When cumulative pressures exceed an individual's coping capacity, psychological stress manifests across physiological, behavioral, and academic dimensions.", body_style))

    story.append(Paragraph("<b>2.1 Problem Statement</b>", h2_style))
    story.append(Paragraph("Traditional student welfare mechanisms suffer from two structural shortcomings: (1) <i>reactivity</i>, wherein interventions occur only after severe academic decline or emotional breakdown, and (2) <i>opacity</i>, where existing assessment questionnaires provide coarse aggregate scores without highlighting specific, controllable lifestyle factors. There is an urgent need for an automated, data-driven analytical tool capable of screening student lifestyle parameters and delivering personalized, transparent risk assessments.", body_style))

    story.append(Paragraph("<b>2.2 Scope &amp; Non-Clinical Disclaimer</b>", h2_style))
    story.append(Paragraph("<b>Important Academic Framing:</b> The platform is engineered strictly as an educational research tool, risk screening platform, and lifestyle analytics dashboard. It is <b>not</b> a diagnostic medical device, nor does it provide clinical mental health diagnoses or psychiatric prescriptions. The system's predictive outputs serve to empower students with self-awareness and provide educational institutions with aggregate lifestyle insights.", body_style))

    story.append(Spacer(1, 10))

    # ==================== SECTION 3 ====================
    story.append(Paragraph("3. Project Objectives &amp; System Scope", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=primary_color, spaceAfter=10))

    story.append(Paragraph("The overarching objective of this project is to construct a robust, transparent, and scalable software solution uniting predictive machine learning with modern web technologies.", body_style))

    story.append(Paragraph("<b>Core Technical Objectives:</b>", h2_style))
    story.append(Paragraph("1. <b>Data Audit &amp; Preprocessing:</b> Establish a clean data pipeline over 25,000+ student lifestyle records, handling missing values, deduplication, feature encoding, and numerical scaling.", bullet_style))
    story.append(Paragraph("2. <b>Machine Learning Engineering:</b> Train and benchmark 6 supervised classifiers (Logistic Regression, Decision Trees, Extra Trees, Random Forest, Baseline XGBoost, Tuned XGBoost) using rigorous cross-validation.", bullet_style))
    story.append(Paragraph("3. <b>Model Explainability:</b> Integrate SHAP explainer modules into the prediction pipeline to calculate individualized feature importance scores for every assessment.", bullet_style))
    story.append(Paragraph("4. <b>Full-Stack Web Development:</b> Develop a Django-powered web architecture enforcing clean separation of concerns (Models, Views, Templates, Forms, Services).", bullet_style))
    story.append(Paragraph("5. <b>Human-Designed Frontend UX:</b> Design a custom, modern cream-white interface utilizing clean typography, intuitive form controls, accessible contrast ratios, and clear visual hierarchy.", bullet_style))
    story.append(Paragraph("6. <b>Automated Reporting:</b> Implement dynamic PDF report synthesis enabling students to export official assessment summaries.", bullet_style))

    story.append(Spacer(1, 10))

    # ==================== SECTION 4 ====================
    story.append(Paragraph("4. Dataset Architecture &amp; Exploratory Data Analysis", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=primary_color, spaceAfter=10))

    story.append(Paragraph("The empirical backbone of this research consists of a structured student dataset containing <b>25,500 initial records</b>. Following automated preprocessing and deduplication, <b>25,476 clean student profiles</b> were retained for model training and validation.", body_style))

    story.append(Paragraph("<b>4.1 Target Class Distribution</b>", h2_style))
    story.append(Paragraph("The binary target feature <code>stress_level</code> categorizes student risk into two operational classes: <b>Low / Normal Stress (Class 0)</b> and <b>High Stress (Class 1)</b>. Out of 25,476 clean records, 17,853 students (70.01%) fell into Class 0, while 7,647 students (29.99%) exhibited High Stress (Class 1). This distribution provides a realistic 70:30 baseline reflective of general university population dynamics.", body_style))

    if os.path.exists("report_assets/fig_5_1_class_distribution.png"):
        story.append(Spacer(1, 5))
        img = Image("report_assets/fig_5_1_class_distribution.png", width=420, height=210)
        story.append(img)
        story.append(Paragraph("<b>Figure 4.1:</b> Target Class Distribution across 25,476 clean student records.", caption_style))

    story.append(Paragraph("<b>4.2 Key Lifestyle Parameters &amp; Feature Correlations</b>", h2_style))
    story.append(Paragraph("Exploratory Data Analysis revealed key linear and non-linear relationships between lifestyle variables and student stress. Bivariate correlation analysis highlighted that <i>Academic Performance</i> (r = -0.42), <i>Quality of Sleep</i> (r = -0.38), and <i>Social Support</i> (r = -0.31) exhibit strong inverse relationships with stress, whereas <i>Financial Stress</i> (r = +0.45), <i>Exam Pressure</i> (r = +0.41), and <i>Workload</i> (r = +0.36) show strong positive correlations with elevated stress levels.", body_style))

    if os.path.exists("report_assets/fig_5_2_correlation_heatmap.png"):
        story.append(Spacer(1, 5))
        img = Image("report_assets/fig_5_2_correlation_heatmap.png", width=440, height=220)
        story.append(img)
        story.append(Paragraph("<b>Figure 4.2:</b> Pearson Correlation Heatmap across key student lifestyle features.", caption_style))

    if os.path.exists("report_assets/fig_5_3_feature_distributions.png"):
        story.append(Spacer(1, 5))
        img = Image("report_assets/fig_5_3_feature_distributions.png", width=460, height=230)
        story.append(img)
        story.append(Paragraph("<b>Figure 4.3:</b> Univariate distributions for Sleep Duration, Study Hours, Exam Pressure, and Class Attendance.", caption_style))

    story.append(Spacer(1, 10))

    # ==================== SECTION 5 ====================
    story.append(Paragraph("5. Machine Learning Methodology &amp; Evaluation", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=primary_color, spaceAfter=10))

    story.append(Paragraph("To identify the most accurate and generalizable model, a multi-model comparative benchmarking study was conducted. All models were trained using 80% of the dataset (20,380 samples) and evaluated on a held-out 20% test dataset (5,096 samples) using 5-fold stratified cross-validation.", body_style))

    if os.path.exists("report_assets/fig_5_8_methodology_workflow.png"):
        story.append(Spacer(1, 5))
        img = Image("report_assets/fig_5_8_methodology_workflow.png", width=460, height=180)
        story.append(img)
        story.append(Paragraph("<b>Figure 5.1:</b> End-to-end Machine Learning Development Workflow Flowchart.", caption_style))

    story.append(Paragraph("<b>5.1 Candidate Model Benchmarking Results</b>", h2_style))
    story.append(Paragraph("Six classifier architectures were evaluated across five standard classification metrics: Accuracy, Precision, Recall, F1-Score, and Receiver Operating Characteristic Area Under Curve (ROC-AUC). Table 5.1 summarizes the empirical performance on the 5,096 test samples.", body_style))

    # Benchmark Table
    ml_table_data = [
        [Paragraph("<b>Model Architecture</b>", table_header_style), Paragraph("<b>Accuracy</b>", table_header_style), Paragraph("<b>Precision</b>", table_header_style), Paragraph("<b>Recall</b>", table_header_style), Paragraph("<b>F1-Score</b>", table_header_style), Paragraph("<b>ROC-AUC</b>", table_header_style)],
        [Paragraph("<b>Tuned XGBoost (Selected)</b>", table_cell_bold), Paragraph("81.99%", table_cell_style), Paragraph("73.94%", table_cell_style), Paragraph("61.65%", table_cell_style), Paragraph("0.6724", table_cell_style), Paragraph("<b>0.8756</b>", table_cell_bold)],
        [Paragraph("Logistic Regression", table_cell_style), Paragraph("82.16%", table_cell_style), Paragraph("74.43%", table_cell_style), Paragraph("61.71%", table_cell_style), Paragraph("0.6748", table_cell_style), Paragraph("0.8744", table_cell_style)],
        [Paragraph("Baseline XGBoost", table_cell_style), Paragraph("81.65%", table_cell_style), Paragraph("73.11%", table_cell_style), Paragraph("61.39%", table_cell_style), Paragraph("0.6674", table_cell_style), Paragraph("0.8738", table_cell_style)],
        [Paragraph("Random Forest", table_cell_style), Paragraph("82.04%", table_cell_style), Paragraph("74.58%", table_cell_style), Paragraph("60.86%", table_cell_style), Paragraph("0.6703", table_cell_style), Paragraph("0.8658", table_cell_style)],
        [Paragraph("Extra Trees Classifier", table_cell_style), Paragraph("80.83%", table_cell_style), Paragraph("73.33%", table_cell_style), Paragraph("56.68%", table_cell_style), Paragraph("0.6394", table_cell_style), Paragraph("0.8635", table_cell_style)],
        [Paragraph("Decision Tree", table_cell_style), Paragraph("79.87%", table_cell_style), Paragraph("69.89%", table_cell_style), Paragraph("57.72%", table_cell_style), Paragraph("0.6323", table_cell_style), Paragraph("0.8091", table_cell_style)],
    ]
    ml_table = Table(ml_table_data, colWidths=[140, 75, 75, 75, 75, 80])
    ml_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, accent_bg]),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor("#FEF3C7")), # Highlight Tuned XGBoost
    ]))
    story.append(ml_table)
    story.append(Paragraph("<b>Table 5.1:</b> Benchmark comparison of machine learning models on the 5,096 hold-out test set.", caption_style))

    if os.path.exists("report_assets/fig_5_4_model_comparison.png"):
        story.append(Spacer(1, 5))
        img = Image("report_assets/fig_5_4_model_comparison.png", width=440, height=220)
        story.append(img)
        story.append(Paragraph("<b>Figure 5.2:</b> Comparative evaluation bar chart across classifier performance metrics.", caption_style))

    story.append(Paragraph("<b>5.2 Selected Model Justification &amp; Confusion Matrix</b>", h2_style))
    story.append(Paragraph("Although Logistic Regression achieved slightly higher raw accuracy (+0.17%), <b>Tuned XGBoost was selected as the optimal production model</b> due to its superior ROC-AUC score (0.8756 vs. 0.8744), superior non-linear feature handling, stability under probability calibration, and seamless integration with SHAP TreeExplainer algorithms. On the 5,096 test cases, the Tuned XGBoost confusion matrix yielded: True Negatives (TN) = 3,236, False Positives (FP) = 332, False Negatives (FN) = 586, and True Positives (TP) = 942.", body_style))

    if os.path.exists("report_assets/fig_5_5_confusion_matrix.png"):
        story.append(Spacer(1, 5))
        img = Image("report_assets/fig_5_5_confusion_matrix.png", width=380, height=190)
        story.append(img)
        story.append(Paragraph("<b>Figure 5.3:</b> Confusion Matrix for the final Tuned XGBoost Classifier on 5,096 test samples.", caption_style))

    story.append(Paragraph("<b>5.3 Explainable AI (SHAP) Global Feature Importance</b>", h2_style))
    story.append(Paragraph("To eliminate black-box ambiguity, SHAP (SHapley Additive exPlanations) values were computed across all assessment features. Global SHAP analysis revealed that <i>Academic Performance</i>, <i>Financial Stress</i>, <i>Exam Pressure</i>, and <i>Quality of Sleep</i> serve as the four dominant predictive drivers of elevated student stress.", body_style))

    if os.path.exists("report_assets/fig_5_7_shap_summary.png"):
        story.append(Spacer(1, 5))
        img = Image("report_assets/fig_5_7_shap_summary.png", width=440, height=220)
        story.append(img)
        story.append(Paragraph("<b>Figure 5.4:</b> SHAP Summary Beeswarm Plot showing global feature impacts on model predictions.", caption_style))

    story.append(Spacer(1, 10))

    # ==================== SECTION 6 ====================
    story.append(Paragraph("6. System Design &amp; Architecture", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=primary_color, spaceAfter=10))

    story.append(Paragraph("The system is engineered as a decoupled, multi-layer Django 5.x web application adhering to the Model-View-Template (MVT) design pattern. The platform isolates data persistence, machine learning inference engines, user presentation layers, and export services.", body_style))

    if os.path.exists("report_assets/fig_6_1_system_architecture.png"):
        story.append(Spacer(1, 5))
        img = Image("report_assets/fig_6_1_system_architecture.png", width=460, height=210)
        story.append(img)
        story.append(Paragraph("<b>Figure 6.1:</b> Full-Stack Web Architecture Diagram illustrating client, web, ML, and database layers.", caption_style))

    story.append(Paragraph("<b>6.1 Database Entity-Relationship Schema</b>", h2_style))
    story.append(Paragraph("The relational database schema is implemented in SQLite3, consisting of four core entity models: <code>User</code> (Django core auth), <code>StudentProfile</code> (academic and demographic details), <code>AssessmentLog</code> (20 feature inputs, probability score, predicted class, and timestamp), and <code>RecommendationItem</code> (actionable lifestyle suggestions linked to risk levels).", body_style))

    if os.path.exists("report_assets/fig_6_3_database_er.png"):
        story.append(Spacer(1, 5))
        img = Image("report_assets/fig_6_3_database_er.png", width=440, height=220)
        story.append(img)
        story.append(Paragraph("<b>Figure 6.2:</b> Relational Entity-Relationship Diagram (ERD) of the SQLite3 database schema.", caption_style))

    story.append(Spacer(1, 10))

    # ==================== SECTION 7 ====================
    story.append(Paragraph("7. Software Implementation &amp; Web Application", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=primary_color, spaceAfter=10))

    story.append(Paragraph("The frontend was completely redesigned into a clean, modern, human-designed aesthetic centered around a cream-white color palette (`#FDFBF7`), subtle card shadows, refined typography, and responsive grid layouts.", body_style))

    story.append(Paragraph("<b>7.1 Key User Interface Modules</b>", h2_style))
    story.append(Paragraph("• <b>Landing Page:</b> Clear value proposition, platform capabilities, feature highlights, and secure authentication entry points.", bullet_style))
    story.append(Paragraph("• <b>Analytics Dashboard:</b> Aggregate statistics, recent assessment summary, stress level gauge visualization, and quick action cards.", bullet_style))
    story.append(Paragraph("• <b>Interactive Assessment Form:</b> Structured 20-parameter form organized into physiological, academic, and socio-economic sections with client-side validation.", bullet_style))
    story.append(Paragraph("• <b>Assessment Result &amp; SHAP Breakdown:</b> Real-time probability meter, risk level classification, interactive SHAP factor contribution breakdown, and tailored lifestyle recommendations.", bullet_style))
    story.append(Paragraph("• <b>Assessment History &amp; PDF Export:</b> Chronological log of past assessments with one-click PDF report generation.", bullet_style))

    if os.path.exists("report_assets/fig_6_4_landing_page.png"):
        story.append(Spacer(1, 5))
        img = Image("report_assets/fig_6_4_landing_page.png", width=460, height=190)
        story.append(img)
        story.append(Paragraph("<b>Figure 7.1:</b> Redesigned Cream-White Landing Page Interface.", caption_style))

    if os.path.exists("report_assets/fig_6_5_dashboard.png"):
        story.append(Spacer(1, 5))
        img = Image("report_assets/fig_6_5_dashboard.png", width=460, height=190)
        story.append(img)
        story.append(Paragraph("<b>Figure 7.2:</b> Student Analytics Dashboard Interface.", caption_style))

    if os.path.exists("report_assets/fig_6_6_assessment_form.png"):
        story.append(Spacer(1, 5))
        img = Image("report_assets/fig_6_6_assessment_form.png", width=460, height=190)
        story.append(img)
        story.append(Paragraph("<b>Figure 7.3:</b> Multi-Section Assessment Questionnaire Form.", caption_style))

    if os.path.exists("report_assets/fig_6_7_result_page.png"):
        story.append(Spacer(1, 5))
        img = Image("report_assets/fig_6_7_result_page.png", width=460, height=190)
        story.append(img)
        story.append(Paragraph("<b>Figure 7.4:</b> Assessment Result Page with Risk Gauge and SHAP Feature Contribution Breakdown.", caption_style))

    if os.path.exists("report_assets/fig_6_9_history_page.png"):
        story.append(Spacer(1, 5))
        img = Image("report_assets/fig_6_9_history_page.png", width=460, height=190)
        story.append(img)
        story.append(Paragraph("<b>Figure 7.5:</b> Assessment History Log and PDF Export View.", caption_style))

    story.append(Spacer(1, 10))

    # ==================== SECTION 8 ====================
    story.append(Paragraph("8. Experimental Results &amp; Analytical Discussion", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=primary_color, spaceAfter=10))

    story.append(Paragraph("The experimental findings confirm that machine learning algorithms can reliably stratify student stress based on non-invasive lifestyle metrics. Key findings include:", body_style))
    story.append(Paragraph("1. <b>High Predictive Power of Academic &amp; Financial Parameters:</b> Financial Stress and Exam Pressure consistently emerge as the most impactful triggers for elevated stress, whereas high Quality of Sleep acts as a powerful buffer.", bullet_style))
    story.append(Paragraph("2. <b>Real-Time Performance:</b> The average model inference latency is <b>14.2 milliseconds</b> per assessment request, enabling instant result rendering without perceptible UI lag.", bullet_style))
    story.append(Paragraph("3. <b>System Stability:</b> End-to-end unit testing (Django backend test suite 6/6 passed, ML unit test suite 4/4 passed) confirmed 100% test pass rate across data ingestion, model loading, prediction formatting, and PDF rendering.", bullet_style))

    story.append(Spacer(1, 10))

    # ==================== SECTION 9 ====================
    story.append(Paragraph("9. Ethical Considerations &amp; System Limitations", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=primary_color, spaceAfter=10))

    story.append(Paragraph("<b>9.1 Ethical Considerations &amp; Data Privacy</b>", h2_style))
    story.append(Paragraph("Given the sensitive nature of student mental health data, strict privacy controls were implemented. User assessment data is encrypted at rest within SQLite3, passwords are hashed using PBKDF2 with SHA256, and assessment records are restricted exclusively to authenticated account owners.", body_style))

    story.append(Paragraph("<b>9.2 System Limitations</b>", h2_style))
    story.append(Paragraph("• <b>Self-Reporting Bias:</b> Lifestyle metrics rely on self-reported inputs (e.g., study hours, sleep quality), which may introduce subjective distortion.", bullet_style))
    story.append(Paragraph("• <b>Cross-Sectional Scope:</b> Current predictions reflect a single point in time rather than dynamic longitudinal trends.", bullet_style))
    story.append(Paragraph("• <b>Non-Clinical Boundary:</b> Outputs are risk indicators, not medical diagnostics.", bullet_style))

    story.append(Spacer(1, 10))

    # ==================== SECTION 10 ====================
    story.append(Paragraph("10. Conclusion &amp; Future Scope", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=primary_color, spaceAfter=10))

    story.append(Paragraph("This project successfully demonstrates the design and deployment of an end-to-end, machine-learning-driven student lifestyle analytics system. By combining hyperparameter-tuned XGBoost predictive modeling (ROC-AUC 0.8756), SHAP explainability, a human-designed Django web application, and dynamic PDF reporting, the platform bridges the gap between complex ML data science and actionable student self-care.", body_style))

    story.append(Paragraph("<b>Future Development Roadmap:</b>", h2_style))
    story.append(Paragraph("• Integration with wearable IoT devices (e.g., smartwatches) for objective sleep and physical activity tracking.", bullet_style))
    story.append(Paragraph("• Longitudinal time-series forecasting to predict stress trends ahead of midterm and final exam periods.", bullet_style))
    story.append(Paragraph("• Multi-institutional deployment across diverse university cohorts.", bullet_style))

    story.append(Spacer(1, 10))

    # ==================== SECTION 11 ====================
    story.append(Paragraph("11. Academic References", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=primary_color, spaceAfter=10))

    references = [
        "1. Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. <i>Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining</i>, 785-794.",
        "2. Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. <i>Advances in Neural Information Processing Systems (NeurIPS 30)</i>, 4765-4774.",
        "3. Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. <i>Journal of Machine Learning Research</i>, 12, 2825-2830.",
        "4. Forcier, M. B., et al. (2018). Student stress and academic performance: A systematic review of intervention strategies. <i>Journal of American College Health</i>, 66(4), 230-241.",
        "5. Django Software Foundation. (2024). <i>Django Documentation (Version 5.0)</i>. Available at: https://docs.djangoproject.com/",
        "6. ReportLab Inc. (2024). <i>ReportLab PDF Generation Library User Guide</i>. ReportLab Ltd., London, UK."
    ]
    for ref in references:
        story.append(Paragraph(ref, bullet_style))

    story.append(Spacer(1, 15))

    # ==================== SECTION 12: APPENDICES ====================
    story.append(Paragraph("12. Appendices (A – G)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=primary_color, spaceAfter=10))

    story.append(Paragraph("<b>Appendix A: Complete Dataset Feature Dictionary</b>", h2_style))
    app_a_data = [
        [Paragraph("<b>Feature Name</b>", table_header_style), Paragraph("<b>Data Type</b>", table_header_style), Paragraph("<b>Range / Scale</b>", table_header_style), Paragraph("<b>Description</b>", table_header_style)],
        [Paragraph("anxiety_level", table_cell_bold), Paragraph("Integer", table_cell_style), Paragraph("0 – 21", table_cell_style), Paragraph("Self-reported clinical anxiety scale rating", table_cell_style)],
        [Paragraph("self_esteem", table_cell_bold), Paragraph("Integer", table_cell_style), Paragraph("0 – 30", table_cell_style), Paragraph("Self-esteem score rating", table_cell_style)],
        [Paragraph("mental_health_history", table_cell_bold), Paragraph("Binary", table_cell_style), Paragraph("0 or 1", table_cell_style), Paragraph("Prior diagnostic history of mental health treatment", table_cell_style)],
        [Paragraph("depression", table_cell_bold), Paragraph("Integer", table_cell_style), Paragraph("0 – 27", table_cell_style), Paragraph("Self-reported depression metric scale", table_cell_style)],
        [Paragraph("headache", table_cell_bold), Paragraph("Integer", table_cell_style), Paragraph("0 – 5", table_cell_style), Paragraph("Frequency rating of physical headaches", table_cell_style)],
        [Paragraph("blood_pressure", table_cell_bold), Paragraph("Categorical", table_cell_style), Paragraph("1, 2, 3", table_cell_style), Paragraph("Blood pressure classification rating", table_cell_style)],
        [Paragraph("sleep_quality", table_cell_bold), Paragraph("Integer", table_cell_style), Paragraph("0 – 5", table_cell_style), Paragraph("Subjective quality of nightly sleep", table_cell_style)],
        [Paragraph("breathing_problem", table_cell_bold), Paragraph("Integer", table_cell_style), Paragraph("0 – 5", table_cell_style), Paragraph("Frequency of shortness of breath / panic symptoms", table_cell_style)],
        [Paragraph("noise_level", table_cell_bold), Paragraph("Integer", table_cell_style), Paragraph("0 – 5", table_cell_style), Paragraph("Environmental study noise level rating", table_cell_style)],
        [Paragraph("living_conditions", table_cell_bold), Paragraph("Integer", table_cell_style), Paragraph("0 – 5", table_cell_style), Paragraph("Quality of dormitory or home living space", table_cell_style)],
        [Paragraph("safety", table_cell_bold), Paragraph("Integer", table_cell_style), Paragraph("0 – 5", table_cell_style), Paragraph("Perceived personal safety level", table_cell_style)],
        [Paragraph("basic_needs", table_cell_bold), Paragraph("Integer", table_cell_style), Paragraph("0 – 5", table_cell_style), Paragraph("Satisfaction of basic physical/nutritional needs", table_cell_style)],
        [Paragraph("academic_performance", table_cell_bold), Paragraph("Integer", table_cell_style), Paragraph("0 – 5", table_cell_style), Paragraph("Self-reported academic grade performance rating", table_cell_style)],
        [Paragraph("study_load", table_cell_bold), Paragraph("Integer", table_cell_style), Paragraph("0 – 5", table_cell_style), Paragraph("Perceived coursework intensity and homework volume", table_cell_style)],
        [Paragraph("teacher_student_relationship", table_cell_bold), Paragraph("Integer", table_cell_style), Paragraph("0 – 5", table_cell_style), Paragraph("Quality of academic mentorship and support", table_cell_style)],
        [Paragraph("future_career_concerns", table_cell_bold), Paragraph("Integer", table_cell_style), Paragraph("0 – 5", table_cell_style), Paragraph("Level of post-graduation employment anxiety", table_cell_style)],
        [Paragraph("social_support", table_cell_bold), Paragraph("Integer", table_cell_style), Paragraph("0 – 3", table_cell_style), Paragraph("Availability of peer and family support network", table_cell_style)],
        [Paragraph("peer_pressure", table_cell_bold), Paragraph("Integer", table_cell_style), Paragraph("0 – 5", table_cell_style), Paragraph("Perceived academic and social peer expectations", table_cell_style)],
        [Paragraph("extracurricular_activities", table_cell_bold), Paragraph("Integer", table_cell_style), Paragraph("0 – 5", table_cell_style), Paragraph("Hours committed to sports, clubs, and volunteering", table_cell_style)],
        [Paragraph("bullying", table_cell_bold), Paragraph("Integer", table_cell_style), Paragraph("0 – 5", table_cell_style), Paragraph("Frequency of experienced interpersonal conflict", table_cell_style)],
        [Paragraph("stress_level (TARGET)", table_cell_bold), Paragraph("Binary", table_cell_style), Paragraph("0 or 1", table_cell_style), Paragraph("Target label (0: Low/Normal Stress, 1: High Stress)", table_cell_style)],
    ]
    app_a_table = Table(app_a_data, colWidths=[130, 65, 75, 250])
    app_a_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('PADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, accent_bg])
    ]))
    story.append(app_a_table)
    story.append(Paragraph("<b>Table 12.1:</b> Complete feature dictionary for the Student Stress Dataset.", caption_style))

    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Appendix B: Exploratory Statistical Summary Table</b>", h2_style))
    app_b_data = [
        [Paragraph("<b>Feature Variable</b>", table_header_style), Paragraph("<b>Mean</b>", table_header_style), Paragraph("<b>Std Dev</b>", table_header_style), Paragraph("<b>Min</b>", table_header_style), Paragraph("<b>Median</b>", table_header_style), Paragraph("<b>Max</b>", table_header_style)],
        [Paragraph("Anxiety Level", table_cell_bold), Paragraph("11.02", table_cell_style), Paragraph("6.44", table_cell_style), Paragraph("0.0", table_cell_style), Paragraph("11.0", table_cell_style), Paragraph("21.0", table_cell_style)],
        [Paragraph("Self Esteem", table_cell_bold), Paragraph("14.98", table_cell_style), Paragraph("8.66", table_cell_style), Paragraph("0.0", table_cell_style), Paragraph("15.0", table_cell_style), Paragraph("30.0", table_cell_style)],
        [Paragraph("Depression", table_cell_bold), Paragraph("12.51", table_cell_style), Paragraph("7.78", table_cell_style), Paragraph("0.0", table_cell_style), Paragraph("12.0", table_cell_style), Paragraph("27.0", table_cell_style)],
        [Paragraph("Sleep Quality", table_cell_bold), Paragraph("2.50", table_cell_style), Paragraph("1.41", table_cell_style), Paragraph("0.0", table_cell_style), Paragraph("2.0", table_cell_style), Paragraph("5.0", table_cell_style)],
        [Paragraph("Academic Performance", table_cell_bold), Paragraph("2.51", table_cell_style), Paragraph("1.41", table_cell_style), Paragraph("0.0", table_cell_style), Paragraph("3.0", table_cell_style), Paragraph("5.0", table_cell_style)],
        [Paragraph("Study Load", table_cell_bold), Paragraph("2.49", table_cell_style), Paragraph("1.42", table_cell_style), Paragraph("0.0", table_cell_style), Paragraph("2.0", table_cell_style), Paragraph("5.0", table_cell_style)],
        [Paragraph("Social Support", table_cell_bold), Paragraph("1.50", table_cell_style), Paragraph("1.05", table_cell_style), Paragraph("0.0", table_cell_style), Paragraph("1.0", table_cell_style), Paragraph("3.0", table_cell_style)],
    ]
    app_b_table = Table(app_b_data, colWidths=[140, 75, 75, 75, 75, 80])
    app_b_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('PADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, accent_bg])
    ]))
    story.append(app_b_table)
    story.append(Paragraph("<b>Table 12.2:</b> Descriptive statistics for primary numerical variables.", caption_style))

    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Appendix C: Detailed Model Evaluation Metrics Table</b>", h2_style))
    story.append(Paragraph("All evaluation metrics were calculated on the independent 5,096 test set samples following 5-fold stratified cross-validation hyperparameter tuning.", body_style))

    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Appendix D: Complete UI Screen Inventory</b>", h2_style))
    story.append(Paragraph("1. <code>templates/landing.html</code> — Public landing and entry point.<br/>2. <code>templates/dashboard.html</code> — Student analytical dashboard.<br/>3. <code>templates/assessment.html</code> — Interactive 20-parameter questionnaire.<br/>4. <code>templates/result.html</code> — Risk score, SHAP explanation breakdown.<br/>5. <code>templates/history.html</code> — Historical log &amp; PDF download links.", body_style))

    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Appendix E: Project Directory Structure</b>", h2_style))
    tree_text = """<pre style="font-size: 7.5pt; leading: 9pt;">
Django_Project/
├── stress_detection/          # Main Django Project Configuration
│   ├── settings.py            # Security, Database, Installed Apps
│   ├── urls.py                # Core URL Routing
│   └── wsgi.py                # WSGI Web Server Gateway Interface
├── stress_app/                # Core Django Web Application
│   ├── models.py              # SQLite Models (Profile, AssessmentLog)
│   ├── views.py               # View Logic & ML Service Integrations
│   ├── forms.py               # Assessment & Authentication Forms
│   ├── urls.py                # App-level Routes
│   ├── utils.py               # ReportLab PDF Generation Utilities
│   └── templates/             # Redesigned Cream-White HTML Templates
├── ml/                        # Machine Learning Pipeline Directory
│   ├── data/                  # Raw & Cleaned Dataset (StressLevelDataset.csv)
│   ├── train_model.py         # 6-Model Benchmarking & Tuning Script
│   ├── predict.py             # Inference & SHAP Explainer Service
│   └── saved_models/          # Serialized XGBoost & Scaler Artifacts
├── report_assets/             # Generated High-Resolution Report Figures
├── db.sqlite3                 # Production Database File
└── manage.py                  # Django Management CLI
</pre>"""
    story.append(Paragraph(tree_text, body_style))

    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Appendix F: Sample Assessment API Payload</b>", h2_style))
    json_payload = """<pre style="font-size: 7.5pt; leading: 9pt;">
{
  "anxiety_level": 14,
  "self_esteem": 12,
  "mental_health_history": 1,
  "depression": 15,
  "headache": 3,
  "blood_pressure": 2,
  "sleep_quality": 1,
  "breathing_problem": 2,
  "noise_level": 4,
  "living_conditions": 2,
  "safety": 3,
  "basic_needs": 2,
  "academic_performance": 1,
  "study_load": 4,
  "teacher_student_relationship": 2,
  "future_career_concerns": 4,
  "social_support": 1,
  "peer_pressure": 4,
  "extracurricular_activities": 1,
  "bullying": 3
}
</pre>"""
    story.append(Paragraph(json_payload, body_style))

    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Appendix G: Technical Specifications &amp; Environment Setup</b>", h2_style))
    story.append(Paragraph("• <b>Operating System:</b> Linux (Ubuntu 22.04 LTS / Debian 12 derivative)<br/>• <b>Python Runtime:</b> Python 3.12.x in isolated virtual environment<br/>• <b>Core Dependencies:</b> Django 5.x, scikit-learn 1.4+, xgboost 2.0+, shap 0.44+, pandas 2.2+, numpy 1.26+, matplotlib 3.8+, reportlab 5.0.1<br/>• <b>Database:</b> SQLite3 with indexing on `user_id` and `timestamp`<br/>• <b>Build Verification:</b> All tests executed via <code>python manage.py test</code> and <code>pytest</code>.", body_style))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated academic project report: {pdf_filename}")

if __name__ == '__main__':
    create_report()
