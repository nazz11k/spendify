from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Friendship
from .serializers import (
    FriendshipSerializer, CreateFriendRequestSerializer
)
from users.models import CustomUser

@extend_schema(tags=["Social"])
class FriendshipViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateFriendRequestSerializer
        return FriendshipSerializer

    @extend_schema(
        summary="List Friends",
        description="Get a list of all accepted friendships.",
        responses={200: FriendshipSerializer(many=True)}
    )
    def list(self, request):
        user = request.user
        friendships = Friendship.objects.filter(
            (Q(from_user=user) | Q(to_user=user)) & Q(status=Friendship.Status.ACCEPTED)
        ).distinct()

        serializer = FriendshipSerializer(friendships, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Send Friend Request",
        description="Send a friend request to another user by ID.",
        request=CreateFriendRequestSerializer,
        responses={201: FriendshipSerializer}
    )
    def create(self, request):
        serializer = CreateFriendRequestSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        to_user = CustomUser.objects.get(id=serializer.validated_data['user_id'])

        friendship = Friendship.objects.create(
            from_user=request.user,
            to_user=to_user
        )

        return Response(
            FriendshipSerializer(friendship).data,
            status=status.HTTP_201_CREATED
        )

    @extend_schema(
        summary="Delete Friend / Cancel Request",
        description="Remove a friend or cancel a pending request sent by you.",
        responses={204: None}
    )
    def destroy(self, request, pk=None):
        try:
            friendship = Friendship.objects.get(
                Q(id=pk) & (Q(from_user=request.user) | Q(to_user=request.user))
            )

            if ((friendship.status == Friendship.Status.PENDING
                and friendship.from_user == request.user)
                    or (friendship.status == Friendship.Status.ACCEPTED)):

                friendship.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {"error": "You can only decline your own request."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Friendship.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="List Pending Requests (Received)",
        description="Get a list of friend requests waiting for your approval.",
        responses={200: FriendshipSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def pending(self, request):
        requests = Friendship.objects.filter(
            to_user=request.user,
            status=Friendship.Status.PENDING
        )
        serializer = FriendshipSerializer(requests, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="List Sent Requests",
        description="Get a list of friend requests you have sent.",
        responses={200: FriendshipSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def sent(self, request):
        requests = Friendship.objects.filter(
            from_user=request.user,
            status=Friendship.Status.PENDING
        )
        serializer = FriendshipSerializer(requests, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Accept Friend Request",
        request=None,
        responses={200: FriendshipSerializer}
    )
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        try:
            friend_request = Friendship.objects.get(
                id=pk,
                to_user=request.user,
                status=Friendship.Status.PENDING
            )
            friend_request.status = Friendship.Status.ACCEPTED
            friend_request.save()
            return Response(FriendshipSerializer(friend_request).data)
        except Friendship.DoesNotExist:
            return Response(
                {"error": "Request does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        summary="Decline Friend Request",
        request=None,
        responses={204: None}
    )
    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        try:
            friend_request = Friendship.objects.get(
                id=pk,
                to_user=request.user,
                status=Friendship.Status.PENDING
            )
            friend_request.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Friendship.DoesNotExist:
            return Response(
                {"error": "Request does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )
