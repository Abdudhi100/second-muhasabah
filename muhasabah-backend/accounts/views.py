from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer, DefaultTodoSerializer, PersonalTodoSerializer
from .throttles import LoginThrottle
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from .models import DefaultTodo, PersonalTodo


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [LoginThrottle]
    throttle_scope = "login"

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = data["user"]
        access = data["access"]
        refresh = data["refresh"]

        # Build response payload
        payload = {
            "user": UserSerializer(user).data,
            "tokens": {"access": access}  # refresh is stored in cookie for security
        }

        response = Response(payload, status=status.HTTP_200_OK)

        # Set HttpOnly cookie for refresh token
        secure_cookie = not settings.DEBUG  # True in production
        response.set_cookie(
            key="refresh_token",
            value=refresh,
            httponly=True,
            secure=secure_cookie,
            samesite="Lax",  # choose "Lax" or "Strict" depending on your needs
            path="/api/auth/token/refresh/",  # scope it to the refresh URL
            max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        )

        return response


class CookieTokenRefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        # Prefer refresh from request body; fall back to cookie
        refresh = request.data.get("refresh") or request.COOKIES.get("refresh_token")
        if not refresh:
            return Response({"detail": "No refresh token provided."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TokenRefreshSerializer(data={"refresh": refresh})
        serializer.is_valid(raise_exception=True)
        access = serializer.validated_data["access"]

        # Optionally rotate and set new refresh cookie if you want rotation (not covered here)
        return Response({"access": access}, status=status.HTTP_200_OK)


# Logout: clear cookie
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = Response({"detail": "Logged out"}, status=status.HTTP_200_OK)
        response.delete_cookie("refresh_token", path="/api/auth/token/refresh/")
        return response
    

class DefaultTodoListView(generics.ListAPIView):
    serializer_class = DefaultTodoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DefaultTodo.objects.all()

class PersonalTodoListCreateView(generics.ListCreateAPIView):
    serializer_class = PersonalTodoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PersonalTodo.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class PersonalTodoDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PersonalTodoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PersonalTodo.objects.filter(owner=self.request.user)
