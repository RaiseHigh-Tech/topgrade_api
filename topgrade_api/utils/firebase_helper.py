"""
Helper functions for Firebase authentication in the API
"""
from topgrade_api.firebase_config import verify_firebase_token, get_user_by_phone

def validate_firebase_phone_auth(id_token):
    """
    Validate Firebase phone authentication token
    
    Args:
        id_token (str): Firebase ID token from Flutter client
        
    Returns:
        tuple: (success: bool, data: dict or error_message: str)
    """
    # Verify the Firebase token
    decoded_token = verify_firebase_token(id_token)
    
    if not decoded_token:
        return False, "Invalid or expired Firebase token"
    
    # Extract phone number from token
    phone_number = decoded_token.get('phone_number')
    
    if not phone_number:
        return False, "Phone number not found in token"
    
    # Remove country code prefix if needed (e.g., +91 -> return just the 10 digits)
    # You can customize this based on your needs
    clean_phone = phone_number.replace('+91', '').replace('+', '')
    
    return True, {
        'phone_number': clean_phone,
        'full_phone': phone_number,
        'uid': decoded_token.get('uid'),
        'firebase_data': decoded_token
    }
