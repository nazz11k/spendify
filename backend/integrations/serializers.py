from rest_framework import serializers
from .models import FinancialAdvice


class FinancialAdviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialAdvice
        fields = ['id', 'created_at', 'advices']


class ReceiptUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()
