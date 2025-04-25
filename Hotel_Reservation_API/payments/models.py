from django.db import models
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from bookings.models import Booking
from django.conf import settings
from accounts.models import User
import time

class PaymentMethod(models.Model):
    name = models.CharField(max_length=100)  
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
    
class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'
    class PaymentMethodChoice(models.TextChoices):
        CREDIT_CARD = 'credit_card', 'Credit Card'
        PAYPAL = 'paypal', 'PayPal'
        BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE,related_name="payment")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments' , null=True , blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50,choices=PaymentMethodChoice.choices)
    transaction_id = models.CharField(max_length=255, unique=True,blank=True, null=True)
    status = models.CharField(max_length=20,  choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    payment_date = models.DateTimeField(default=timezone.now)
    is_deposit = models.BooleanField(default=False) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment #{self.pk} - {self.amount} | {self.get_status_display()}"
    
    def mark_as_completed(self, transaction_id=None):
        self.status = self.PaymentStatus.COMPLETED
        time = int(time.time())
        if transaction_id:
            self.transaction_id = transaction_id
        else:
            self.transaction_id = f"PAY-{self.pk}-{time}"
        self.save()
    
    def mark_as_failed(self):
        self.status = self.PaymentStatus.FAILED
        self.save()
    
    def refund(self):
        self.status = self.PaymentStatus.REFUNDED
        self.save()
    
    class Meta:
        db_table = "payments"
        ordering = ['-created_at']

class PaymentSettings(models.Model):
    require_deposit = models.BooleanField(default=True)  # Whether a deposit is required
    deposit_percentage = models.IntegerField(
        default=30, 
        validators=[
            MinValueValidator(30, message="Minimum deposit percentage must be at least 30%"),
            MaxValueValidator(100, message="Deposit percentage cannot exceed 100%")
        ]
    ) 
    allow_card_payment = models.BooleanField(default=True)
    allow_paypal = models.BooleanField(default=True)
    allow_bank_transfer = models.BooleanField(default=True)

    def calculate_deposit(self, total_amount):
        if not self.require_deposit:
            return Decimal('0.00')
        return (Decimal(self.deposit_percentage) / Decimal('100')) * Decimal(total_amount)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.require_deposit and self.deposit_percentage < 30:
            raise ValidationError({"deposit_percentage": "Minimum deposit percentage must be at least 30%"})
        

class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    user = models.ForeignKey(User, on_delete=models.CASCADE , related_name='payments', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    transaction_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    is_deposit = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
            self.transaction_id = f"TXN-{self.booking.id}-{timestamp}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.amount}"