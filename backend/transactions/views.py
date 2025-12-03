from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Category, Transaction
from .serializers import (
    CategorySerializer, TransactionSerializer
)


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

@extend_schema_view(
    list=extend_schema(
        summary="List all categories",
        description="Returns standard categories (global) and personal user categories."
    ),
    create=extend_schema(
        summary="Create a category",
        description="Creates a new personal category for the user."
    ),
    retrieve=extend_schema(summary="Get category details"),
    update=extend_schema(
        summary="Update a category",
        description="Updates a personal category. Standard categories cannot be edited."
    ),
    partial_update=extend_schema(summary="Patch a category"),
    destroy=extend_schema(
        summary="Delete a category",
        description="Deletes a personal category. Standard categories cannot be deleted."
    )
)
@extend_schema(tags=["Transactions: Categories"])
class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(
            Q(owner=self.request.user) | Q(owner=None)
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.owner is None:
            raise PermissionDenied("Ви не можете редагувати стандартні категорії.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.owner is None:
            raise PermissionDenied("Ви не можете видаляти стандартні категорії.")
        instance.delete()

@extend_schema_view(
    list=extend_schema(
        summary="List transactions",
        description="Get a list of all personal transactions."
    ),
    create=extend_schema(
        summary="Create transaction",
        description="Record a new income or expense."
    ),
    retrieve=extend_schema(summary="Get transaction details"),
    update=extend_schema(summary="Update transaction"),
    partial_update=extend_schema(summary="Patch transaction"),
    destroy=extend_schema(summary="Delete transaction")
)
@extend_schema(tags=["Transactions: Core"])
class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Transaction.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_context(self):
        return {'request': self.request}
