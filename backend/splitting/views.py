from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse

from .models import SharedSpent, SharedSpentMember
from .serializers import SharedSpentSerializer
from django.db.models import Q


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user

@extend_schema(tags=["Splitting"])
@extend_schema_view(
    list=extend_schema(
        summary="List shared spents",
        description="Shows spents where you are the owner or a participant."
    ),
    create=extend_schema(
        summary="Create shared spent",
        description="Create a new bill split with other users."
    ),
    retrieve=extend_schema(summary="Get shared spent details"),
    update=extend_schema(summary="Update shared spent"),
    destroy=extend_schema(
        summary="Delete shared spent",
        description="Only the owner can delete the shared spent completely."
    )
)
class SharedSpentViewSet(viewsets.ModelViewSet):
    serializer_class = SharedSpentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return SharedSpent.objects.filter(
            Q(owner=self.request.user) | Q(participants__user=self.request.user)
        ).distinct()

    def get_permissions(self):
        if self.action == 'leave_spent':
            return [permissions.IsAuthenticated()]

        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @extend_schema(
        summary="Leave shared spent",
        description="Allows a participant to leave the shared spent. Their share amount is returned to the owner.",
        request=None,
        responses={
            200: OpenApiResponse(description="Successfully left the spent"),
            400: OpenApiResponse(description="Bad request (e.g. owner trying to leave)")
        }
    )
    @action(detail=True, methods=['post'], url_path='leave')
    @transaction.atomic
    def leave_spent(self, request, pk=None):
        shared_spent = self.get_object()
        user = request.user

        if shared_spent.owner == user:
            return Response(
                {"error": "Owner can not leave the spent, only delete it."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            member_part = SharedSpentMember.objects.get(
                shared_spent=shared_spent,
                user=user
            )
            owner_part = SharedSpentMember.objects.get(
                shared_spent=shared_spent,
                is_owner_part=True
            )

            owner_part.amount += member_part.amount
            owner_part.save()

            member_part.delete()

            return Response(
                {"status": "You left this spent."},
                status=status.HTTP_200_OK
            )
        except SharedSpentMember.DoesNotExist:
            return Response(
                {"error": "You are not participant of this spent."},
                status=status.HTTP_400_BAD_REQUEST
            )
