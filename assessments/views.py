import sys
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Assessment
from .forms import AssessmentForm

# Add ml/src to Python path for ML inference imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ml', 'src'))
try:
    from predict import predict_stress
    from explain import explain_prediction
except ImportError:
    # Fallback import if running within module path
    from ml.src.predict import predict_stress
    from ml.src.explain import explain_prediction


from .services import get_assessment_analysis
from .feedback import generate_personalized_feedback


@login_required
def new_assessment_view(request):
    if request.method == 'POST':
        form = AssessmentForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.user = request.user

            # Prepare feature dictionary for ML pipeline / FastAPI service
            input_dict = {
                'Student_Type': assessment.student_type,
                'Sleep_Hours': float(assessment.sleep_hours),
                'Study_Hours': float(assessment.study_hours),
                'Social_Media_Hours': float(assessment.social_media_hours),
                'Attendance': float(assessment.attendance),
                'Exam_Pressure': float(assessment.exam_pressure),
                'Family_Support': float(assessment.family_support),
                'Month': float(assessment.month),
            }

            try:
                # Trigger unified ML & SHAP analysis service (FastAPI with local failover)
                analysis_result = get_assessment_analysis(input_dict)

                assessment.predicted_stress_level = analysis_result['prediction_code']
                assessment.predicted_label = analysis_result['predicted_label']
                assessment.probability_low_stress = analysis_result['probabilities']['low_normal_stress']
                assessment.probability_high_stress = analysis_result['probabilities']['high_stress']
                assessment.model_version = analysis_result['model_version']
                assessment.top_contributing_factors = analysis_result['top_contributing_factors']
                assessment.narrative_explanation = analysis_result['narrative_explanation']

                assessment.save()
                messages.success(request, "Assessment submitted successfully! Here is your AI analysis.")
                return redirect('assessments:result', pk=assessment.pk)

            except Exception as e:
                messages.error(request, f"An error occurred during prediction processing: {str(e)}")
    else:
        form = AssessmentForm()

    return render(request, 'assessments/new_assessment.html', {'form': form})



def _get_assessment_feedback(assessment: Assessment):
    input_dict = {
        'Student_Type': assessment.student_type,
        'Sleep_Hours': assessment.sleep_hours,
        'Study_Hours': assessment.study_hours,
        'Social_Media_Hours': assessment.social_media_hours,
        'Attendance': assessment.attendance,
        'Exam_Pressure': assessment.exam_pressure,
        'Family_Support': assessment.family_support,
        'Month': assessment.month,
    }
    return generate_personalized_feedback(input_dict, assessment.predicted_stress_level)


@login_required
def assessment_result_view(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk, user=request.user)
    feedback_list = _get_assessment_feedback(assessment)
    return render(request, 'assessments/result.html', {
        'assessment': assessment,
        'feedback_list': feedback_list
    })


@login_required
def assessment_history_view(request):
    assessments = Assessment.objects.filter(user=request.user)
    return render(request, 'assessments/history.html', {'assessments': assessments})


@login_required
def assessment_detail_view(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk, user=request.user)
    feedback_list = _get_assessment_feedback(assessment)
    return render(request, 'assessments/detail.html', {
        'assessment': assessment,
        'feedback_list': feedback_list
    })


from django.http import HttpResponse
from .reports import generate_assessment_pdf


@login_required
def export_pdf_report_view(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk, user=request.user)
    pdf_buffer = generate_assessment_pdf(assessment)
    
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="StressLens_Report_#{assessment.pk}.pdf"'
    return response



