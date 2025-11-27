from ninja import NinjaAPI
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from topgrade_api.schemas import LoginSchema, SignupSchema, RequestOtpSchema, VerifyOtpSchema, ResetPasswordSchema, PhoneSigninSchema, RefreshTokenSchema
from topgrade_api.models import CustomUser, OTPVerification
from topgrade_api.utils.firebase_helper import validate_firebase_phone_auth
from django.utils import timezone
import time

# Initialize Django Ninja API for authentication
auth_api = NinjaAPI(version="1.0.0", title="Authentication API", urls_namespace="auth")

@auth_api.post("/signin")
def signin(request, credentials: LoginSchema):
    """
    Simple signin API that returns access_token and refresh_token
    """
    user = authenticate(username=credentials.email, password=credentials.password)
    
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return {
            "success": True,
            "message": "Signin successful",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "has_area_of_intrest": bool(user.area_of_intrest and user.area_of_intrest.strip())
        }
    else:
        return JsonResponse({"message": "Invalid credentials"}, status=401)

@auth_api.post("/signup")
def signup(request, user_data: SignupSchema):
    """
    User registration API
    """
    # Check if passwords match
    if user_data.password != user_data.confirm_password:
        return JsonResponse({"message": "Passwords do not match"}, status=400)
    
    # Check if user already exists
    if CustomUser.objects.filter(email=user_data.email).exists():
        return JsonResponse({"message": "User with this email already exists"}, status=400)
    
    try:
        # Create new user
        user = CustomUser.objects.create_user(
            email=user_data.email,
            password=user_data.password,
            fullname=user_data.fullname
        )
        
        # Generate tokens for immediate login
        refresh = RefreshToken.for_user(user)
        
        return {
            "success": True,
            "message": "User created successfully",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "has_area_of_intrest": bool(user.area_of_intrest and user.area_of_intrest.strip())
        }
    except Exception as e:
        return JsonResponse({"message": "Error creating user"}, status=500)

@auth_api.post("/request-otp")
def request_otp(request, otp_data: RequestOtpSchema):
    """
    Request OTP for password reset
    """
    try:
        # Check if user exists
        user = CustomUser.objects.get(email=otp_data.email)
        
        # Create or update OTP verification record
        otp_verification, created = OTPVerification.objects.get_or_create(
            email=otp_data.email,
            defaults={'is_verified': False}
        )
        
        # Reset verification status for new OTP request
        if not created:
            otp_verification.is_verified = False
            otp_verification.verified_at = None
            otp_verification.expires_at = timezone.now() + timezone.timedelta(minutes=10)
            otp_verification.save()
        
        return {
            "success": True,
            "message": "OTP sent successfully",
        }
        
    except CustomUser.DoesNotExist:
        return JsonResponse({"message": "User with this email does not exist"}, status=404)
    except Exception as e:
        return JsonResponse({"message": "Error sending OTP"}, status=500)

@auth_api.post("/verify-otp")
def verify_otp(request, verify_data: VerifyOtpSchema):
    """
    Verify OTP for password reset
    """
    try:
        # Check if user exists
        user = CustomUser.objects.get(email=verify_data.email)
        
        # Check if OTP verification record exists
        try:
            otp_verification = OTPVerification.objects.get(email=verify_data.email)
        except OTPVerification.DoesNotExist:
            return JsonResponse({"message": "No OTP request found. Please request OTP first."}, status=400)
        
        # Check if OTP verification has expired
        if otp_verification.is_expired():
            return JsonResponse({"message": "OTP has expired. Please request a new OTP."}, status=400)
        
        # Check if OTP is correct (static OTP: 654321)
        if verify_data.otp != "654321":
            return JsonResponse({"message": "Invalid OTP"}, status=400)
        
        # Mark OTP as verified
        otp_verification.is_verified = True
        otp_verification.verified_at = timezone.now()
        otp_verification.save()
        
        return {
            "success": True,
            "message": "OTP verified successfully",
        }
        
    except CustomUser.DoesNotExist:
        return JsonResponse({"message": "User with this email does not exist"}, status=404)
    except Exception as e:
        return JsonResponse({"message": "Error verifying OTP"}, status=500)

@auth_api.post("/reset-password")
def reset_password(request, reset_data: ResetPasswordSchema):
    """
    Reset password API - allows users to reset their password using email, password, and confirm password
    """
    # Check if passwords match
    if reset_data.new_password != reset_data.confirm_password:
        return JsonResponse({"message": "Passwords do not match"}, status=400)
    
    try:
        # Check if user exists
        user = CustomUser.objects.get(email=reset_data.email)
        
        # Check if OTP was verified
        try:
            otp_verification = OTPVerification.objects.get(email=reset_data.email)
        except OTPVerification.DoesNotExist:
            return JsonResponse({"message": "OTP verification required. Please request and verify OTP first."}, status=400)
        
        # Check if OTP verification is still valid and verified
        if not otp_verification.is_verified:
            return JsonResponse({"message": "OTP not verified. Please verify OTP before resetting password."}, status=400)
        
        if otp_verification.is_expired():
            return JsonResponse({"message": "OTP verification has expired. Please request a new OTP."}, status=400)
        
        # Update the password
        user.set_password(reset_data.new_password)
        user.save()
        
        # Clean up the OTP verification record after successful password reset
        otp_verification.delete()
        
        return {
            "success": True,
            "message": "Password reset successfully"
        }
        
    except CustomUser.DoesNotExist:
        return JsonResponse({"message": "User with this email does not exist"}, status=404)
    except Exception as e:
        return JsonResponse({"message": "Error resetting password"}, status=500)

@auth_api.post("/phone-signin")
def phone_signin(request, phone_data: PhoneSigninSchema):
    """
    Firebase Phone Authentication - Verify Firebase token and create/login user
    This endpoint is used by Flutter mobile app after Firebase OTP verification
    
    Request format:
    {
        "name": "User Full Name",
        "phoneNumber": "+911234567890",
        "firebaseToken": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjFlMDNkN..."
    }
    """
    # Validate Firebase token
    success, result = validate_firebase_phone_auth(phone_data.firebaseToken)
    
    if not success:
        return JsonResponse({"message": result}, status=401)
    
    phone_number = result['phone_number']
    
    try:
        # Check if user exists with this phone number
        user = CustomUser.objects.get(phone_number=phone_number)
        message = "Phone signin successful"
        
    except CustomUser.DoesNotExist:
        # Create new user if doesn't exist
        # Validate that name is provided for new users
        if not phone_data.name or not phone_data.name.strip():
            return JsonResponse({
                "message": "Full name is required for new users. Please provide your name.",
                "user_exists": False
            }, status=400)
        
        try:
            # Generate unique email with Firebase UID
            firebase_uid = result.get('uid', str(int(time.time())))
            temp_email = f"{phone_number}+{firebase_uid}@phone.com"
            
            # Double check email uniqueness
            counter = 1
            while CustomUser.objects.filter(email=temp_email).exists():
                temp_email = f"{phone_number}+{firebase_uid}_{counter}@phone.com"
                counter += 1
            
            # Create user with provided name
            user = CustomUser.objects.create_user(
                email=temp_email,
                phone_number=phone_number,
                fullname=phone_data.name.strip(),
                password=phone_number  # Use phone number as password
            )
            message = "User created and signed in successfully"
            
        except Exception as e:
            return JsonResponse({"message": f"Error creating user: {str(e)}"}, status=500)
    
    try:
        # Generate JWT tokens for login
        refresh = RefreshToken.for_user(user)
        
        return {
            "success": True,
            "message": message,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "has_area_of_intrest": bool(user.area_of_intrest and user.area_of_intrest.strip())
        }
        
    except Exception as e:
        return JsonResponse({"message": f"Error during phone signin: {str(e)}"}, status=500)

@auth_api.post("/refresh")
def refresh_token(request, token_data: RefreshTokenSchema):
    """
    Refresh access token using refresh token
    """
    try:
        # Create RefreshToken object from the provided refresh token
        refresh = RefreshToken(token_data.refresh_token)
        
        # Generate new access token
        new_access_token = str(refresh.access_token)
        
        return {
            "success": True,
            "message": "Token refreshed successfully",
            "access_token": new_access_token
        }
        
    except Exception as e:
        return JsonResponse({"message": "Invalid or expired refresh token"}, status=401)