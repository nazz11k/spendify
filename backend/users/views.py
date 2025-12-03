from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import CustomUser
from .serializers import RegisterSerializer, UserSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse

@extend_schema(
    tags=["Auth"],
    summary="Register a new user",
    description="Creates a new user account with a linked profile. Returns the created user data.",
    responses={
        201: UserSerializer,
        400: OpenApiResponse(description="Validation error (e.g. email exists)")
    }
)
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
