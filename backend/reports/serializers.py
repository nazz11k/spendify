from rest_framework import serializers


class UnifiedTransactionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    date = serializers.DateField()
    category_name = serializers.CharField()
    description = serializers.CharField(allow_blank=True, allow_null=True)

    source_id = serializers.IntegerField(help_text="transaction ID or SharedSpentMember ID")
    filter_fields = ['date_from', 'date_to', 'category']


class CategorySummarySerializer(serializers.Serializer):
    category = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    percentage = serializers.FloatField()
    transaction_count = serializers.IntegerField()


class TimeSeriesSerializer(serializers.Serializer):
    date = serializers.DateField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
