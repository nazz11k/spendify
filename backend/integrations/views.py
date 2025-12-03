from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
import logging
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .llm_service import get_ai_advice
from .serializers import FinancialAdviceSerializer, ReceiptUploadSerializer
from .services import scan_receipt
from .models import FinancialAdvice
from transactions.models import Transaction, Category
from transactions.serializers import TransactionSerializer

logger = logging.getLogger(__name__)


@extend_schema(tags=["Integrations: OCR"])
class ScanReceiptView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ReceiptUploadSerializer

    @extend_schema(
        summary="Scan Receipt Image",
        description="Upload an image of a receipt. The system will extract data (amount, date, category) and create a transaction.",
        request=ReceiptUploadSerializer,
        responses={
            201: TransactionSerializer,
            400: OpenApiResponse(description="Invalid image or request"),
            503: OpenApiResponse(description="AI Service unavailable")
        }
    )
    def post(self, request, *args, **kwargs):
        if 'image' not in request.FILES:
            return Response({"error": "No image provided"}, status=400)

        image_file = request.FILES['image']

        try:
            ai_data = scan_receipt(image_file)
        except Exception as e:
            logger.error(f"AI Service Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=503)

        ai_category_name = ai_data.get('category', 'Other')
        category = self._find_standard_category(ai_category_name)

        description = ai_data.get('description')
        if not description:
            description = f"Scanned receipt from {ai_data.get('date', 'unknown date')}"

        with transaction.atomic():
            new_transaction = Transaction.objects.create(
                owner=request.user,
                category=category,
                amount=ai_data.get('amount', 0.0),
                date=ai_data.get('date') or None,
                description=description[:500]
            )

        return Response(
            TransactionSerializer(new_transaction).data,
            status=status.HTTP_201_CREATED
        )

    def _find_standard_category(self, name):
        category = Category.objects.filter(
            owner=None,
            name__iexact=name
        ).first()

        if category:
            return category

        fallback = Category.objects.filter(owner=None, name__in=["Other"]).first()

        if fallback:
            return fallback

        return Category.objects.create(name="Other", type="EXPENSE", owner=None)


@extend_schema(tags=["Integrations: AI Advice"])
class FinancialAdviceView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get Advice History",
        description="Returns a list of all previously generated financial reports.",
        responses={200: FinancialAdviceSerializer(many=True)}
    )
    def get(self, request):
        reports = FinancialAdvice.objects.filter(user=request.user)
        serializer = FinancialAdviceSerializer(reports, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Generate New Advice",
        description="Analyzes user transactions for the last 30 days and generates new financial advice using LLM.",
        request=None,
        responses={
            201: FinancialAdviceSerializer,
            400: OpenApiResponse(description="Not enough data"),
            503: OpenApiResponse(description="AI Service unavailable")
        }
    )
    def post(self, request):
        user = request.user
        logger.info(f"Generating NEW advice for user {user.id}...")

        stats = self._get_statistics(user)

        advice_text = get_ai_advice(stats['comparison_data'], stats['transactions_for_ai'])

        if not stats['comparison_data']:
            return Response(
                {"detail": "Not enough data to generate advice."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if advice_text is None:
            return Response(
                {"detail": "AI service is currently unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            advice_text = get_ai_advice(stats['comparison_data'], stats['transactions_for_ai'])
        except Exception as e:
            logger.error(f"AI Service error: {e}")
            return Response(
                {"detail": "Сервіс ШІ тимчасово недоступний."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        report = FinancialAdvice.objects.create(
            user=user,
            advices=advice_text
        )

        return Response(
            FinancialAdviceSerializer(report).data,
            status=status.HTTP_201_CREATED
        )

    def _get_statistics(self, user):
        now = timezone.now()
        start_current = now - timedelta(days=30)
        start_previous = start_current - timedelta(days=30)

        current_qs = Transaction.objects.filter(
            owner=user, date__gte=start_current, date__lte=now
        ).select_related('category').order_by('-date')

        prev_qs = Transaction.objects.filter(
            owner=user, date__gte=start_previous, date__lt=start_current
        )

        curr_map = {i['category__name']: float(i['total']) for i in
                    current_qs.values('category__name').annotate(total=Sum('amount'))}
        prev_map = {i['category__name']: float(i['total']) for i in
                    prev_qs.values('category__name').annotate(total=Sum('amount'))}

        all_categories = set(curr_map.keys()) | set(prev_map.keys())
        comparison_data = {}

        for cat in all_categories:
            val_curr = curr_map.get(cat, 0.0)
            val_prev = prev_map.get(cat, 0.0)

            if val_prev > 0:
                diff_percent = ((val_curr - val_prev) / val_prev) * 100
            else:
                diff_percent = 100.0 if val_curr > 0 else 0.0

            comparison_data[cat] = {
                'current': val_curr,
                'previous': val_prev,
                'diff_percent': diff_percent
            }

        transactions_for_ai = []
        for t in current_qs:
            transactions_for_ai.append({
                'date': t.date.strftime('%Y-%m-%d') if t.date else 'N/A',
                'amount': float(t.amount),
                'category_name': t.category.name if t.category else 'Other',
                'description': t.description or ''
            })

        return {
            "comparison_data": comparison_data,
            "transactions_for_ai": transactions_for_ai
        }
