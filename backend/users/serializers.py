from rest_framework import serializers
from django.db import transaction
from .models import CustomUser, Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            'first_name', 'last_name', 'gender',
            'avatar', 'contact_details'
        )


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = CustomUser
        fields = ('pk', 'email', 'username', 'profile')
        read_only_fields = ('email', 'username')

    @transaction.atomic
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        profile = instance.profile

        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return super().update(instance, validated_data)


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )
    password_confirm = serializers.CharField(
        write_only=True
    )

    first_name = serializers.CharField(
        max_length=100,
        write_only=True
    )
    last_name = serializers.CharField(
        max_length=100,
        write_only=True
    )
    gender = serializers.ChoiceField(
        choices=Profile.Gender.choices,
        required=False,
        default=Profile.Gender.NA,
        write_only=True
    )

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("User with this username already exists.")
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    @transaction.atomic
    def create(self, validated_data):
        user_data = {
            'email': validated_data['email'],
            'username': validated_data['username'],
            'password': validated_data['password'],
        }

        profile_data = {
            'first_name': validated_data['first_name'],
            'last_name': validated_data['last_name'],
            'gender': validated_data.get('gender', Profile.Gender.NA),
        }

        user = CustomUser.objects.create_user(**user_data)

        Profile.objects.filter(user=user).update(**profile_data)

        return user
