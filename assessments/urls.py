from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    path('new/', views.new_assessment_view, name='new'),
    path('result/<int:pk>/', views.assessment_result_view, name='result'),
    path('history/', views.assessment_history_view, name='history'),
    path('detail/<int:pk>/', views.assessment_detail_view, name='detail'),
    path('export-pdf/<int:pk>/', views.export_pdf_report_view, name='export_pdf'),
]

