from django.db import models
from django.contrib.auth.models import User


class Assessment(models.Model):
    STUDENT_TYPE_CHOICES = [
        ('college', 'College Student'),
        ('school', 'School Student'),
        ('working_student', 'Working Student'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessments')
    student_type = models.CharField(max_length=30, choices=STUDENT_TYPE_CHOICES, default='college')
    
    sleep_hours = models.FloatField(help_text="Average daily sleep hours (e.g., 2.0 to 10.0)")
    study_hours = models.FloatField(help_text="Average daily study hours")
    social_media_hours = models.FloatField(help_text="Average daily social media usage hours")
    attendance = models.FloatField(help_text="Academic attendance percentage (0 to 100%)")
    exam_pressure = models.FloatField(help_text="Perceived exam pressure rating (0 to 10)")
    family_support = models.FloatField(help_text="Perceived family support rating (0 to 10)")
    month = models.IntegerField(help_text="Academic month (1 to 12)")

    # ML Output Attributes
    predicted_stress_level = models.IntegerField(help_text="0 for Low/Normal Stress, 1 for High Stress")
    predicted_label = models.CharField(max_length=50, default="Low/Normal Stress")
    probability_low_stress = models.FloatField(default=0.0)
    probability_high_stress = models.FloatField(default=0.0)
    
    top_contributing_factors = models.JSONField(default=list, blank=True)
    narrative_explanation = models.TextField(blank=True)
    model_version = models.CharField(max_length=50, default="stresslens_v1.0.0")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Assessment #{self.id} for {self.user.username} - {self.predicted_label} ({self.created_at.strftime('%Y-%m-%d')})"
