from typing import Dict, Any, List


def generate_personalized_feedback(input_data: Dict[str, Any], predicted_stress_level: int) -> List[Dict[str, str]]:
    """
    Generates rule-based, non-clinical lifestyle feedback recommendations based on student assessment inputs
    and predicted stress level.

    Parameters:
        input_data (Dict[str, Any]): Dictionary of student lifestyle inputs.
        predicted_stress_level (int): 0 for Low/Normal Stress, 1 for High Stress.

    Returns:
        List[Dict[str, str]]: List of personalized recommendation cards.
    """
    feedback = []

    sleep_hours = float(input_data.get('Sleep_Hours', 7.0))
    study_hours = float(input_data.get('Study_Hours', 5.0))
    social_media_hours = float(input_data.get('Social_Media_Hours', 2.0))
    attendance = float(input_data.get('Attendance', 85.0))
    exam_pressure = float(input_data.get('Exam_Pressure', 5.0))
    family_support = float(input_data.get('Family_Support', 7.0))

    # 1. Sleep Hygiene Rule
    if sleep_hours < 6.5:
        feedback.append({
            'category': 'Sleep Hygiene',
            'level': 'warning',
            'icon': 'fa-solid fa-bed',
            'title': 'Prioritize Restorative Sleep',
            'suggestion': f'Your reported sleep duration ({sleep_hours:.1f} hrs) is below the recommended 7–9 hours for students. Try establishing a consistent bedtime routine and avoiding screens 30 minutes before sleep.'
        })
    elif sleep_hours >= 7.5:
        feedback.append({
            'category': 'Sleep Hygiene',
            'level': 'success',
            'icon': 'fa-solid fa-circle-check',
            'title': 'Healthy Sleep Habit',
            'suggestion': f'Your reported sleep ({sleep_hours:.1f} hrs) aligns with optimal recovery guidelines. Maintaining regular sleep patterns strongly supports cognitive focus.'
        })

    # 2. Exam Pressure Rule
    if exam_pressure >= 7.0:
        feedback.append({
            'category': 'Exam Stress Management',
            'level': 'warning',
            'icon': 'fa-solid fa-brain',
            'title': 'Manage Exam Anxiety',
            'suggestion': f'High perceived exam pressure ({exam_pressure:.1f}/10) is a major stress driver. Break large exam topics into smaller daily tasks and utilize practice mock questions.'
        })

    # 3. Study Workload Rule
    if study_hours > 8.0:
        feedback.append({
            'category': 'Workload Balance',
            'level': 'info',
            'icon': 'fa-solid fa-book-open-reader',
            'title': 'Pace Study Intervals',
            'suggestion': f'High daily study duration ({study_hours:.1f} hrs) can cause cognitive fatigue. Implement the Pomodoro technique (50 minutes study / 10 minutes active break) to sustain focus.'
        })

    # 4. Social Support Rule
    if family_support < 5.0:
        feedback.append({
            'category': 'Social Wellbeing',
            'level': 'info',
            'icon': 'fa-solid fa-users',
            'title': 'Strengthen Support System',
            'suggestion': f'Your reported support score is {family_support:.1f}/10. Connecting with study groups, campus peer mentors, or student advisors can help share academic challenges.'
        })

    # 5. Screen Time / Social Media Rule
    if social_media_hours >= 4.0:
        feedback.append({
            'category': 'Digital Wellbeing',
            'level': 'warning',
            'icon': 'fa-solid fa-mobile-screen-button',
            'title': 'Moderate Screen Time',
            'suggestion': f'Higher social media usage ({social_media_hours:.1f} hrs) can contribute to mental clutter. Consider setting App Limits during core study and evening hours.'
        })

    # 6. Attendance & Academic Engagement Rule
    if attendance < 75.0:
        feedback.append({
            'category': 'Academic Engagement',
            'level': 'warning',
            'icon': 'fa-solid fa-user-check',
            'title': 'Boost Class Attendance',
            'suggestion': f'Your reported attendance is {attendance:.1f}%. Attending lectures regularly reduces last-minute exam pressure and improves course material comprehension.'
        })

    # Positive General Encouragement if low stress
    if predicted_stress_level == 0 and not feedback:
        feedback.append({
            'category': 'General Wellbeing',
            'level': 'success',
            'icon': 'fa-solid fa-award',
            'title': 'Balanced Lifestyle Indicators',
            'suggestion': 'Your reported habits reflect a healthy balance between sleep, academic engagement, and personal support. Keep up your current daily routine!'
        })

    return feedback
