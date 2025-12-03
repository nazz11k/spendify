import django_filters
from transactions.models import Transaction


class ReportFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte', label='Date From (YYYY-MM-DD)')
    date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte', label='Date To (YYYY-MM-DD)')
    category = django_filters.NumberFilter(field_name='category', label='Category ID')
    type = django_filters.ChoiceFilter(
        choices=[('personal', 'Personal'), ('shared', 'Shared')],
        label='Transaction Type',
        method='filter_noop'
    )

    class Meta:
        model = Transaction
        fields = ['date_from', 'date_to', 'category']

    def filter_noop(self, queryset, name, value):
        return queryset
