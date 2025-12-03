from django.urls import path
from .views import ScanReceiptView, FinancialAdviceView

urlpatterns = [
    path('scan/', ScanReceiptView.as_view(), name='scan-receipt'),
    path('advice/', FinancialAdviceView.as_view(), name='financial-advice'),
]
