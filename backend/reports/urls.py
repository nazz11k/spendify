from django.urls import path
from .views import ActivityReportView, CategorySummaryView, OverTimeReportView

urlpatterns = [
    path('activity/', ActivityReportView.as_view(), name='activity-report'),
    path('by-category/', CategorySummaryView.as_view(), name='category-report'),
    path('over-time/', OverTimeReportView.as_view(), name='time-report'),
]
