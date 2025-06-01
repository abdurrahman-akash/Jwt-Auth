import uuid
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings

from .serializers import (
    RegisterSerializer, 
    LoginSerializer, 
    UserSerializer, 
    PasswordResetSerializer, 
    PasswordResetConfirmSerializer, 
    BaseSerializer,
)
from .models import CustomUser
from Auth.base import NewAPIView
from .utils import send_verification_email, send_password_reset_email

class RegisterView(NewAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate and save verification code
        verification_code = uuid.uuid4().hex
        user.verification_code = verification_code
        user.verification_code_expiry = timezone.now() + timedelta(minutes=30)
        user.is_active = False
        user.save()

        send_verification_email(user, verification_code)

        return Response(
            {"message": "Registration successful. Please check your email to verify."},
            status=status.HTTP_201_CREATED
        )

class VerifyEmailView(NewAPIView):
    permission_classes = [AllowAny]
    serializer_class = BaseSerializer

    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return redirect(f"{settings.FRONTEND_URL}/error?message=Missing verification code")

        try:
            user = CustomUser.objects.get(verification_code=code)
            if user.verification_code_expiry < timezone.now():
                return redirect(f"{settings.FRONTEND_URL}/error?message=Verification code expired")

            user.is_active = True
            user.email_verified = True
            user.verification_code = None
            user.verification_code_expiry = None
            user.save()

            return redirect(f"{settings.FRONTEND_URL}/login?verified=1")
        except CustomUser.DoesNotExist:
            return redirect(f"{settings.FRONTEND_URL}/error?message=Invalid verification code")

class LoginView(NewAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = CustomUser.objects.get(email=email)
            if not user.check_password(password):
                return Response({'error': 'Invalid credentials'}, status=400)
            if not user.email_verified:
                return Response({'error': 'Please verify your email before logging in.'}, status=403)
            if not user.email_verified:
                # Generate new verification code and expiry
                user.verification_code = uuid.uuid4().hex
                user.verification_code_expiry = timezone.now() + timedelta(minutes=30)
                user.save()
                send_verification_email(user, user.verification_code)
                return Response(
                    {'error': 'Please verify your email. A new verification link has been sent.'},
                    status=403
                )
            # If using JWT, generate token here
            return Response({
                'uuid': str(user.id),
                'email': user.email,
                'role': user.role,
                'message': 'Login successful'
            })
        except CustomUser.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=400)

class PasswordResetView(NewAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = CustomUser.objects.get(email=email)
            reset_token = uuid.uuid4().hex
            user.reset_token = reset_token
            user.reset_token_expires = timezone.now() + timedelta(minutes=30)
            user.save()
            send_password_reset_email(user, reset_token)
            return Response({'message': 'Password reset link sent to your email'})
        except CustomUser.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=400)

class PasswordResetConfirmView(NewAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            user = CustomUser.objects.get(reset_token=token)
            if user.reset_token_expires > timezone.now():
                user.set_password(new_password)
                user.reset_token = None
                user.reset_token_expires = None
                user.save()
                return Response({'message': 'Password reset successfully'})
            return Response({'error': 'Reset token expired'}, status=400)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Invalid reset token'}, status=400)

class UserListAPIView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_summary="List all users (Admin only)",
        operation_description="Retrieve a list of all users. This endpoint is restricted to admin users.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class UserDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'

    @swagger_auto_schema(
        operation_summary="Get user details (Admin only)",
        operation_description="Retrieve details of a specific user by their ID. This endpoint is restricted to admin users.",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description="ID of the user to retrieve",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)