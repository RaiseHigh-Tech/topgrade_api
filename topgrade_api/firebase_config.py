"""
Firebase Admin SDK Configuration for OTP Verification
"""
import firebase_admin
from firebase_admin import credentials, auth
from django.conf import settings
import os

# Initialize Firebase Admin SDK
def initialize_firebase():
    """
    Initialize Firebase Admin SDK with service account credentials
    """
    if not firebase_admin._apps:
        # Path to your Firebase service account key JSON file
        cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
        
        try:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK initialized successfully")
        except Exception as e:
            print(f"Error initializing Firebase Admin SDK: {e}")
            # If credentials file not found, you can initialize without credentials for development
            # firebase_admin.initialize_app()

def verify_firebase_token(id_token):
    """
    Verify Firebase ID token from Flutter app
    
    Args:
        id_token (str): Firebase ID token from Flutter client
        
    Returns:
        dict: Decoded token containing user info (phone_number, uid, etc.)
        None: If token is invalid
    """
    try:
        # Verify the ID token
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except auth.InvalidIdTokenError:
        print("Invalid Firebase ID token")
        return None
    except auth.ExpiredIdTokenError:
        print("Firebase ID token has expired")
        return None
    except Exception as e:
        print(f"Error verifying Firebase token: {e}")
        return None

def get_user_by_phone(phone_number):
    """
    Get Firebase user by phone number
    
    Args:
        phone_number (str): Phone number with country code (e.g., +919876543210)
        
    Returns:
        UserRecord: Firebase user record
        None: If user not found
    """
    try:
        user = auth.get_user_by_phone_number(phone_number)
        return user
    except auth.UserNotFoundError:
        return None
    except Exception as e:
        print(f"Error getting user by phone: {e}")
        return None

def verify_phone_number(phone_number, verification_code):
    """
    Note: Firebase Admin SDK doesn't directly verify OTP codes.
    OTP verification happens on the client side (Flutter app).
    
    The server only verifies the ID token that the client receives
    after successful OTP verification.
    
    This function is kept for reference/documentation purposes.
    """
    pass
