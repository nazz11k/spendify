from django.contrib import admin
from .models import FinancialAdvice


@admin.register(FinancialAdvice)
class FinancialAdviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__email', 'advices')
    readonly_fields = ('created_at',)
