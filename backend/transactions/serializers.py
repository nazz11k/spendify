from rest_framework import serializers
from .models import Category, Transaction


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'owner']
        read_only_fields = ['owner']


class TransactionSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'owner', 'category', 'amount',
            'date', 'description'
        ]

    def validate_category(self, category):
        user = self.context['request'].user
        if category.owner is not None and category.owner != user:
            raise serializers.ValidationError(
                "That`s not your category"
            )
        return category
