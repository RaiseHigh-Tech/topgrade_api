"""
Purchase and payment-related API views
"""
from django.http import JsonResponse
from django.utils import timezone
from ..schemas import PurchaseSchema
from ..models import Program, UserPurchase, UserCourseProgress
import random
import string
from .common import api, AuthBearer

@api.post("/purchase", auth=AuthBearer())
def purchase_course(request, data: PurchaseSchema):
    """
    Purchase a program with dummy payment gateway
    Uses unified Program model - works for both regular and advanced programs
    """
    try:
        user = request.auth
        
        # Get request data from schema
        program_id = data.program_id
        payment_method = data.payment_method  # card, upi, wallet, etc.
        
        # Validate input
        if not program_id:
            return JsonResponse({"success": False, "message": "program_id is required"}, status=400)
        
        # Get the program from unified model
        try:
            program = Program.objects.get(id=program_id)
        except Program.DoesNotExist:
            return JsonResponse({"success": False, "message": "Program not found"}, status=404)
        
        # Check if user already purchased this program
        existing_purchase = UserPurchase.objects.filter(
            user=user,
            program=program,
            status='completed'
        ).first()
        
        if existing_purchase:
            return JsonResponse({
                "success": False, 
                "message": "You have already purchased this course"
            }, status=400)
        
        # Calculate final price using the model property
        original_price = program.price
        discount_percentage = program.discount_percentage
        final_price = program.discounted_price
        
        # Generate dummy transaction ID
        transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        
        # Dummy Payment Gateway Processing
        payment_success = dummy_payment_gateway(
            amount=final_price,
            payment_method=payment_method,
            transaction_id=transaction_id
        )
        
        if not payment_success:
            return JsonResponse({
                "success": False,
                "message": "Payment failed. Please try again.",
                "transaction_id": transaction_id
            }, status=400)
        
        # Create purchase record
        purchase = UserPurchase.objects.create(
            user=user,
            program=program,
            amount_paid=final_price,
            purchase_date=timezone.now(),
            status='completed'  # Since payment was successful
        )
        
        # Create initial course progress tracking
        UserCourseProgress.objects.get_or_create(
            user=user,
            purchase=purchase,
            defaults={
                'total_topics': sum(s.topics.count() for s in program.syllabuses.all()),
                'completed_topics': 0,
                'in_progress_topics': 0,
                'completion_percentage': 0.0,
                'is_completed': False,
                'total_watch_time_seconds': 0,
                'last_activity_at': timezone.now()
            }
        )
        
        return {
            "success": True,
            "message": "Course purchased successfully!",
            "pricing": {
                "original_price": float(original_price),
                "discount_percentage": float(discount_percentage),
                "discounted_price": float(final_price),
                "savings": float(original_price - final_price)
            },
            "purchase": {
                "id": purchase.id,
                "program_title": program.title,
                "program_category": program.category.name if program.category else None,
                "purchase_date": purchase.purchase_date.isoformat(),
                "status": purchase.status,
                "amount_paid": float(purchase.amount_paid),
                "transaction_id": transaction_id
            }
        }
        
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error processing purchase: {str(e)}"}, status=500)

def dummy_payment_gateway(amount, payment_method, transaction_id):
    """
    Dummy payment gateway implementation
    Returns True for successful payment, False for failed payment
    """
    # Simulate payment processing delay
    import time
    time.sleep(0.5)
    
    # Dummy logic: 90% success rate, 10% failure rate
    success_rate = 0.9
    random_value = random.random()
    
    if random_value <= success_rate:
        # Payment successful
        print(f"[DUMMY PAYMENT] SUCCESS - Transaction ID: {transaction_id}, Amount: ₹{amount}, Method: {payment_method}")
        return True
    else:
        # Payment failed
        print(f"[DUMMY PAYMENT] FAILED - Transaction ID: {transaction_id}, Amount: ₹{amount}, Method: {payment_method}")
        return False