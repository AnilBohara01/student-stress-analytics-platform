from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from assessments.models import Assessment


@login_required
def home_view(request):
    user_assessments = Assessment.objects.filter(user=request.user)
    latest_assessment = user_assessments.first()
    total_count = user_assessments.count()

    metrics = user_assessments.aggregate(
        avg_sleep=Avg('sleep_hours'),
        avg_study=Avg('study_hours'),
        avg_exam_pressure=Avg('exam_pressure'),
        avg_attendance=Avg('attendance')
    )

    high_stress_count = user_assessments.filter(predicted_stress_level=1).count()
    low_stress_count = user_assessments.filter(predicted_stress_level=0).count()

    context = {
        'latest_assessment': latest_assessment,
        'recent_assessments': user_assessments[:5],
        'total_count': total_count,
        'high_stress_count': high_stress_count,
        'low_stress_count': low_stress_count,
        'metrics': metrics,
    }
    return render(request, 'dashboard/home.html', context)


@login_required
def analytics_view(request):
    user_assessments = Assessment.objects.filter(user=request.user).order_by('created_at')
    total_count = user_assessments.count()

    latest_assessment = user_assessments.last() if total_count > 0 else None
    previous_assessment = user_assessments[total_count - 2] if total_count >= 2 else None

    deltas = {}
    if latest_assessment and previous_assessment:
        deltas = {
            'sleep': latest_assessment.sleep_hours - previous_assessment.sleep_hours,
            'study': latest_assessment.study_hours - previous_assessment.study_hours,
            'exam_pressure': latest_assessment.exam_pressure - previous_assessment.exam_pressure,
            'attendance': latest_assessment.attendance - previous_assessment.attendance,
            'family_support': latest_assessment.family_support - previous_assessment.family_support,
            'stress_prob': (latest_assessment.probability_high_stress - previous_assessment.probability_high_stress) * 100
        }

    metrics = user_assessments.aggregate(
        avg_sleep=Avg('sleep_hours'),
        avg_study=Avg('study_hours'),
        avg_exam_pressure=Avg('exam_pressure'),
        avg_attendance=Avg('attendance'),
        avg_support=Avg('family_support')
    )

    context = {
        'user_assessments': user_assessments,
        'latest_assessment': latest_assessment,
        'previous_assessment': previous_assessment,
        'deltas': deltas,
        'total_count': total_count,
        'metrics': metrics
    }
    return render(request, 'dashboard/analytics.html', context)


def landing_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return render(request, 'pages/landing.html')

