from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, F, Value, CharField
from datetime import datetime, timedelta
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, inline_serializer
from rest_framework import serializers

from .filters import ReportFilter
from transactions.models import Transaction
from splitting.models import SharedSpentMember
from .serializers import (
    UnifiedTransactionSerializer,
    CategorySummarySerializer,
    TimeSeriesSerializer
)


class BaseReportView(generics.GenericAPIView):
    """
    Base view containing common logic for filtering and aggregating data
    from both Transaction (personal) and SharedSpentMember (shared) models.
    """
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    filterset_class = ReportFilter

    queryset = Transaction.objects.none()

    def get_filtered_querysets(self, request):
        user = request.user

        filterset = self.filterset_class(request.GET, queryset=Transaction.objects.none())

        if filterset.is_valid():
            params = filterset.form.cleaned_data
        else:
            params = {}

        date_from = params.get('date_from')
        date_to = params.get('date_to')
        category_val = params.get('category')
        report_type = params.get('type')

        show_personal = report_type in [None, '', 'personal']
        show_shared = report_type in [None, '', 'shared']

        personal_qs = Transaction.objects.filter(owner=user) if show_personal else Transaction.objects.none()
        shared_qs = SharedSpentMember.objects.filter(user=user) if show_shared else SharedSpentMember.objects.none()

        if date_from:
            personal_qs = personal_qs.filter(date__gte=date_from)
            shared_qs = shared_qs.filter(shared_spent__date__gte=date_from)

        if date_to:
            personal_qs = personal_qs.filter(date__lte=date_to)
            shared_qs = shared_qs.filter(shared_spent__date__lte=date_to)

        if category_val:
            cat_id = category_val.id if hasattr(category_val, 'id') else category_val

            personal_qs = personal_qs.filter(category_id=cat_id)
            shared_qs = shared_qs.filter(shared_spent__category_id=cat_id)

        if show_personal:
            personal_qs = personal_qs.annotate(
                report_type=Value('personal', output_field=CharField()),
                cat_name=F('category__name')
            )

        if show_shared:
            shared_qs = shared_qs.annotate(
                report_type=Value('shared', output_field=CharField()),
                date=F('shared_spent__date'),
                cat_name=F('shared_spent__category__name'),
                description=F('shared_spent__description')
            )

        return personal_qs, shared_qs


class ActivityReportView(BaseReportView):
    """
    Endpoint for retrieving a chronological feed of all financial activities.
    """

    @extend_schema(
        summary="Get Activity Feed",
        description=(
                "Returns a combined list of personal transactions and shared expenses "
                "sorted by date (descending). Supports filtering by date range, category, and type."
        ),
        responses={200: UnifiedTransactionSerializer(many=True)},
        tags=["Reports"]
    )
    def get(self, request, *args, **kwargs):
        personal_qs, shared_qs = self.get_filtered_querysets(request)

        combined_data = []

        for t in personal_qs:
            combined_data.append({
                'id': t.id,
                'source_id': t.id,
                'type': 'personal',
                'amount': t.amount,
                'date': t.date,
                'category_name': t.cat_name or 'Other',
                'description': t.description
            })

        for s in shared_qs:
            combined_data.append({
                'id': s.id,
                'source_id': s.id,
                'type': 'shared',
                'amount': s.amount,
                'date': s.date,
                'category_name': s.cat_name or 'Other',
                'description': s.description
            })

        combined_data.sort(key=lambda x: x['date'], reverse=True)

        serializer = UnifiedTransactionSerializer(combined_data, many=True)
        return Response(serializer.data)


class CategorySummaryView(BaseReportView):
    """
    Endpoint for retrieving expenses aggregated by category.
    Ideal for Pie Charts.
    """

    @extend_schema(
        summary="Get Expenses by Category",
        description="Aggregates expenses by category and calculates percentages for the selected period.",
        responses={
            200: inline_serializer(
                name='CategoryReportResponse',
                fields={
                    'total_spent': serializers.DecimalField(max_digits=12, decimal_places=2),
                    'breakdown': CategorySummarySerializer(many=True)
                }
            )
        },
        tags=["Reports"]
    )
    def get(self, request, *args, **kwargs):
        personal_qs, shared_qs = self.get_filtered_querysets(request)

        category_totals = {}
        total_period_spent = 0

        for t in personal_qs:
            cat = t.cat_name or 'Other'
            amount = float(t.amount)
            category_totals[cat] = category_totals.get(cat, 0) + amount
            total_period_spent += amount

        for s in shared_qs:
            cat = s.cat_name or 'Other'
            amount = float(s.amount)
            category_totals[cat] = category_totals.get(cat, 0) + amount
            total_period_spent += amount

        result_data = []
        for cat, amount in category_totals.items():
            percent = (amount / total_period_spent * 100) if total_period_spent > 0 else 0
            result_data.append({
                'category': cat,
                'total_amount': amount,
                'percentage': round(percent, 2),
                'transaction_count': 0
            })

        result_data.sort(key=lambda x: x['total_amount'], reverse=True)

        return Response({
            "total_spent": total_period_spent,
            "breakdown": CategorySummarySerializer(result_data, many=True).data
        })


class OverTimeReportView(BaseReportView):
    """
    Endpoint for retrieving daily spending dynamics.
    Ideal for Line Charts.
    """

    @extend_schema(
        summary="Get Spending Over Time",
        description="Returns total daily spending for the selected period. Fills missing days with 0.0.",
        responses={200: TimeSeriesSerializer(many=True)},
        tags=["Reports"]
    )
    def get(self, request, *args, **kwargs):
        personal_qs, shared_qs = self.get_filtered_querysets(request)

        daily_totals = {}

        for t in personal_qs:
            date_str = t.date.isoformat()
            daily_totals[date_str] = daily_totals.get(date_str, 0) + float(t.amount)

        for s in shared_qs:
            date_str = s.date.isoformat()
            daily_totals[date_str] = daily_totals.get(date_str, 0) + float(s.amount)

        filterset = self.filterset_class(request.GET, queryset=Transaction.objects.none())
        d_from, d_to = None, None

        if filterset.is_valid():
            d_from = filterset.form.cleaned_data.get('date_from')
            d_to = filterset.form.cleaned_data.get('date_to')

        if not d_to:
            d_to = timezone.now().date()
        if not d_from:
            d_from = d_to - timedelta(days=30)

        result_list = []
        delta = d_to - d_from

        for i in range(delta.days + 1):
            day = d_from + timedelta(days=i)
            day_str = day.isoformat()
            result_list.append({
                'date': day,
                'total_amount': daily_totals.get(day_str, 0.0)
            })

        return Response(TimeSeriesSerializer(result_list, many=True).data)