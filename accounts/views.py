from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, UpdateProfileSerializer, ChangePasswordSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
from .utils import api_response, LoginRateThrottle


class RegisterView(APIView):
    # Anyone can register — no token required
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response("error", "Registration failed.", serializer.errors, 400)

        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        return api_response(
            "success",
            "Account created successfully.",
            {
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            201,
        )


class LoginView(APIView):
    # Anyone can attempt login — no token required
    permission_classes = (AllowAny,)
    # Strict rate limit — only 5 login attempts per minute per IP
    throttle_classes = (LoginRateThrottle,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return api_response("error", "Login failed.", serializer.errors, 400)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return api_response(
            "success",
            "Login successful.",
            {
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
        )


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return api_response("error", "Refresh token is required.", None, 400)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return api_response("error", "Invalid or expired token.", None, 400)

        return api_response("success", "Logged out successfully.")


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return api_response(
            "success",
            "Profile retrieved.",
            UserSerializer(request.user).data,
        )

    def patch(self, request):
        serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)
        if not serializer.is_valid():
            return api_response("error", "Update failed.", serializer.errors, 400)
        serializer.save()
        return api_response("success", "Profile updated.", UserSerializer(request.user).data)


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return api_response("error", "Password change failed.", serializer.errors, 400)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return api_response("success", "Password changed successfully.")


class ForgotPasswordView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response("error", "Request failed.", serializer.errors, 400)
        try:
            serializer.send_otp()
        except Exception:
            return api_response("error", "Failed to send OTP email. Please try again later.", None, 500)
        return api_response("success", "OTP sent to your email. It expires in 10 minutes.")


class ResetPasswordView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response("error", "Password reset failed.", serializer.errors, 400)
        user = serializer.validated_data['user']
        otp_obj = serializer.validated_data['otp_obj']
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        otp_obj.is_used = True
        otp_obj.save()
        return api_response("success", "Password reset successfully.")
