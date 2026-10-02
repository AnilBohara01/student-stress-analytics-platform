from django import forms
from .models import Assessment


class AssessmentForm(forms.ModelForm):
    MONTH_CHOICES = [(i, f"Month {i}") for i in range(1, 13)]

    month = forms.ChoiceField(choices=MONTH_CHOICES, initial=6, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Assessment
        fields = [
            'student_type',
            'sleep_hours',
            'study_hours',
            'social_media_hours',
            'attendance',
            'exam_pressure',
            'family_support',
            'month',
        ]
        widgets = {
            'student_type': forms.Select(attrs={'class': 'form-select'}),
            'sleep_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '24', 'placeholder': 'e.g. 7.0'}),
            'study_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '24', 'placeholder': 'e.g. 5.5'}),
            'social_media_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '24', 'placeholder': 'e.g. 2.0'}),
            'attendance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '100', 'placeholder': 'e.g. 85.0'}),
            'exam_pressure': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0', 'max': '10', 'placeholder': 'Scale 0 - 10'}),
            'family_support': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0', 'max': '10', 'placeholder': 'Scale 0 - 10'}),
        }
        labels = {
            'student_type': 'Student Category',
            'sleep_hours': 'Daily Sleep (Hours)',
            'study_hours': 'Daily Study (Hours)',
            'social_media_hours': 'Social Media Usage (Hours)',
            'attendance': 'Academic Attendance (%)',
            'exam_pressure': 'Perceived Exam Pressure (0 - 10)',
            'family_support': 'Family Support Level (0 - 10)',
            'month': 'Current Academic Month',
        }
