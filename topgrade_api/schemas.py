from ninja import Schema

class LoginSchema(Schema):
    email: str
    password: str

class SignupSchema(Schema):
    fullname: str
    email: str
    password: str
    confirm_password: str

class RequestOtpSchema(Schema):
    email: str

class VerifyOtpSchema(Schema):
    email: str
    otp: str

class ResetPasswordSchema(Schema):
    email: str
    new_password: str
    confirm_password: str

class RequestPhoneOtpSchema(Schema):
    phone_number: str

class PhoneSigninSchema(Schema):
    phone_number: str
    otp: str

class RefreshTokenSchema(Schema):
    refresh_token: str

class AreaOfInterestSchema(Schema):
    area_of_intrest: str

class PurchaseSchema(Schema):
    program_type: str  # 'program' or 'advanced_program'
    program_id: int
    payment_method: str = 'card'  # optional, defaults to 'card'

class BookmarkSchema(Schema):
    program_type: str  # 'program' or 'advanced_program'
    program_id: int

class UpdateProgressSchema(Schema):
    topic_id: int
    topic_type: str  # 'topic' or 'advance_topic'
    watch_time_seconds: int
    total_duration_seconds: int = None  # optional