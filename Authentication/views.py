from multiprocessing import Value
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from django.urls import reverse
from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import RefreshToken

from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer, UserSerializer, BaseSerializer
from .models import BlacklistedToken, CustomUser
from Auth.base import NewAPIView

from Authentication import serializers



class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserListAPIView(generics.ListAPIView):
    """
    API endpoint to list all users. Only accessible by admin users.
    """
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
    """
    API endpoint to get details of a specific user. Only accessible by admin users.
    """
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

    
class RegisterView(NewAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate and save verification code
        verification_code = get_random_string(length=32)
        user.verification_code = verification_code
        user.verification_code_expiry = timezone.now() + timedelta(minutes=5)
        user.is_active = False  # Ensure user is inactive until verified
        user.save()

        # Build verification link
        verification_link = request.build_absolute_uri(
            reverse('verify-email')
        ) + f"?code={verification_code}"

        # Email content
        email_subject = "Email Verification"
        email_body_plain = f"Verify your email: {verification_link}"
        email_body_html = f"""
            <p>Click <a href="{verification_link}">here</a> to verify your email.</p>
        """

        # Send email
        send_mail(
            email_subject,
            email_body_plain,
            settings.EMAIL_HOST_USER,
            [user.email],
            html_message=email_body_html,
        )

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
            
            # Check if code is expired
            if user.verification_code_expiry < timezone.now():
                return redirect(f"{settings.FRONTEND_URL}/error?message=Verification code expired")

            # Activate user and mark as verified
            user.is_active = True
            user.email_verified = True
            user.verification_code = None
            user.verification_code_expiry = None
            user.save()

            # Redirect to frontend home page
            return Response({"message": "User verified successfully."}, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid verification code"}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(NewAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer
    
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = CustomUser.objects.get(email=email)
            token = get_random_string(length=32)
            user.reset_token = token
            user.reset_token_expires = timezone.now() + timedelta(minutes=5)
            user.save()
            
            # Your email sending logic here
            return Response({'message': 'Password reset link sent to your email'})
        except CustomUser.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=400)

class PasswordResetConfirmView(NewAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
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
