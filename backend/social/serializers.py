from rest_framework import serializers
from .models import Friendship
from users.models import CustomUser
from django.db.models import Q


class FriendUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email')


class FriendshipSerializer(serializers.ModelSerializer):
    from_user = FriendUserSerializer(read_only=True)
    to_user = FriendUserSerializer(read_only=True)

    class Meta:
        model = Friendship
        fields = ('id', 'from_user', 'to_user', 'status', 'created_at')


class CreateFriendRequestSerializer(serializers.Serializer):

    user_id = serializers.IntegerField()

    def validate_user_id(self, value):
        user = self.context['request'].user

        if not CustomUser.objects.filter(id=value).exists():
            raise serializers.ValidationError("User with this ID does not exist.")

        if user.id == value:
            raise serializers.ValidationError("You can not send frendship request to you.")

        if Friendship.objects.filter(
                (Q(from_user=user, to_user_id=value) | Q(from_user_id=value, to_user=user))
        ).exists():
            raise serializers.ValidationError("Friendship request already exists.")

        return value
