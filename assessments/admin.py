from django.contrib import admin
from .models import Assessment

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'student_type',
        'predicted_label',
        'probability_high_stress',
        'probability_low_stress',
        'created_at'
    )
    list_filter = ('predicted_label', 'student_type', 'created_at')
    search_fields = ('user__username', 'user__email', 'predicted_label')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
