from rest_framework import serializers
from django.db import transaction
from .models import SharedSpent, SharedSpentMember
from users.models import CustomUser
from transactions.models import Category


class ParticipantSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)

    def validate_user_id(self, user_id):
        if not CustomUser.objects.filter(id=user_id).exists():
            raise serializers.ValidationError("User does not exist.")
        return user_id


class SharedSpentSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True, write_only=True, required=True)

    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SharedSpent
        fields = [
            'id', 'owner', 'category', 'total_amount', 'date',
            'description', 'participants', 'created_at'
        ]

    def validate_category(self, category):
        user = self.context['request'].user
        if category.owner is not None and category.owner != user:
            raise serializers.ValidationError("That`s not your category.")
        if category.type != Category.CategoryType.EXPENSE:
            raise serializers.ValidationError("Only expenses can be shared.")
        return category

    def validate_participants(self, participants):
        if not participants:
            raise serializers.ValidationError("There should be at least one participant.")

        user_ids = [p['user_id'] for p in participants]
        if self.context['request'].user.id in user_ids:
            raise serializers.ValidationError("You can not be a participant of your own spent.")

        return participants

    def validate(self, data):
        total_amount = data['total_amount']
        participants_sum = sum(p['amount'] for p in data['participants'])

        if participants_sum > total_amount:
            raise serializers.ValidationError(
                {"participants": "Participants total amount exceeds Expense amount."}
            )

        if (total_amount - participants_sum) < 0.01:
            raise serializers.ValidationError(
                {"total_amount": "Owner`s amount should be at least 0.01."}
            )

        return data

    @transaction.atomic
    def create(self, validated_data):
        participants_data = validated_data.pop('participants')
        owner = validated_data.get('owner')

        shared_spent = SharedSpent.objects.create(**validated_data)

        participants_sum = sum(p['amount'] for p in participants_data)
        owner_amount = validated_data['total_amount'] - participants_sum

        members_to_create = []

        members_to_create.append(
            SharedSpentMember(
                shared_spent=shared_spent,
                user=owner,
                amount=owner_amount,
                is_owner_part=True
            )
        )

        for p in participants_data:
            members_to_create.append(
                SharedSpentMember(
                    shared_spent=shared_spent,
                    user_id=p['user_id'],
                    amount=p['amount'],
                    is_owner_part=False
                )
            )

        SharedSpentMember.objects.bulk_create(members_to_create)

        return shared_spent
