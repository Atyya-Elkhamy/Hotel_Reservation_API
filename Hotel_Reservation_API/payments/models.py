from django.db import models
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from bookings.models import Booking
from django.conf import settings
from accounts.models import User
import time

    
class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
    class PaymentMethodChoice(models.TextChoices):
        CREDIT_CARD = 'credit_card', 'Credit Card'
        PAYPAL = 'paypal', 'PayPal'
        BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE,related_name="payment")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments' , null=True , blank=True)
    hotel = models.ForeignKey("hotels.Hotel", on_delete=models.CASCADE, related_name="payments", null=True, blank=True )
    room = models.ForeignKey("hotels.Room", on_delete=models.CASCADE, related_name="payments", null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50,choices=PaymentMethodChoice.choices , default=PaymentMethodChoice.CREDIT_CARD)
    transaction_id = models.CharField(max_length=255, unique=True,blank=True, null=True)
    status = models.CharField(max_length=20,  choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    payment_date = models.DateTimeField(default=timezone.now)
    is_deposit = models.BooleanField(default=False) 
    first_name = models.CharField(max_length=100 ,default="", blank=True, null=True)
    last_name = models.CharField(max_length=100 ,default="", blank=True, null=True)
    email = models.EmailField(default="", blank=True, null=True)
    phone = models.CharField(max_length=20 , default="", blank=True, null=True)
    address = models.TextField(default="", blank=True, null=True)
    city = models.CharField(max_length=100, default="", blank=True, null=True)
    region = models.CharField(max_length=100 , default="", blank=True, null=True)

    def calculate_deposit(self, total_amount):
        if not self.is_deposit:
            return Decimal('0.00')
        return (Decimal(self.is_deposit) / Decimal('100')) * Decimal(total_amount)
    
    
    def mark_as_completed(self, transaction_id=None):
        self.status = self.PaymentStatus.COMPLETED
        time = int(time.time())
        if transaction_id:
            self.transaction_id = transaction_id
        else:
            self.transaction_id = f"PAY-{self.pk}-{time}"
        self.save()
    
    def __str__(self):
        return f"Payment #{self.pk} - {self.amount} | {self.get_status_display()}"
    class Meta:
        db_table = "payments"



# class PaymentMethod(models.Model):
#     name = models.CharField(max_length=100)  
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     def __str__(self):
#         return self.name

# class PaymentSettings(models.Model):
#     require_deposit = models.BooleanField(default=True)  # Whether a deposit is required
#     deposit_percentage = models.IntegerField(
#         default=30, 
#         validators=[
#             MinValueValidator(30, message="Minimum deposit percentage must be at least 30%"),
#             MaxValueValidator(100, message="Deposit percentage cannot exceed 100%")
#         ]
#     ) 
#     allow_card_payment = models.BooleanField(default=True)
#     allow_paypal = models.BooleanField(default=True)
#     allow_bank_transfer = models.BooleanField(default=True)

#     def calculate_deposit(self, total_amount):
#         if not self.require_deposit:
#             return Decimal('0.00')
#         return (Decimal(self.deposit_percentage) / Decimal('100')) * Decimal(total_amount)
    
#     def clean(self):
#         from django.core.exceptions import ValidationError
        
#         if self.require_deposit and self.deposit_percentage < 30:
#             raise ValidationError({"deposit_percentage": "Minimum deposit percentage must be at least 30%"})
        

# class Payment(models.Model):
#     booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
#     user = models.ForeignKey(User, on_delete=models.CASCADE , related_name='payments', null=True, blank=True)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     payment_date = models.DateTimeField(default=timezone.now)
#     transaction_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
#     is_deposit = models.BooleanField(default=False)

#     def save(self, *args, **kwargs):
#         if not self.transaction_id:
#             timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
#             self.transaction_id = f"TXN-{self.booking.id}-{timestamp}"
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"Payment {self.transaction_id} - {self.amount}"
    

# class Order(models.Model):
#     STATUS_CHOICES = (
#         ('pending', 'قيد الانتظار'),
#         ('confirmed', 'تم التأكيد'),
#         ('cancelled', 'تم الإلغاء'),
#         ('completed', 'مكتمل'),
#     )
#     PAYMENT_METHOD_CHOICES = (
#         ('credit_card', 'بطاقة ائتمان'),
#         ('cash_on_delivery', 'الدفع عند الاستلام'),
#     )

#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
#     club = models.ForeignKey(ClubsModel, on_delete=models.CASCADE, related_name='orders', null=True)
#     total_price = models.DecimalField(max_digits=10, decimal_places=2)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
#     payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)

#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     email = models.EmailField()
#     phone = models.CharField(max_length=20)
#     address = models.TextField()
#     city = models.CharField(max_length=100)
#     region = models.CharField(max_length=100)
#     postal_code = models.CharField(max_length=20)
#     notes = models.TextField(blank=True, null=True)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def _str_(self):
#         return f"Order #{self.id} - {self.user.username}"

# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
#     product = models.ForeignKey(ProductsModel, on_delete=models.SET_NULL, null=True, blank=True)
#     service = models.ForeignKey(ServicesModel, on_delete=models.SET_NULL, null=True, blank=True)
#     quantity = models.PositiveIntegerField(default=1)
#     price = models.DecimalField(max_digits=10, decimal_places=2)

#     def _str_(self):
#         if self.product:
#             return f"{self.product.title} ({self.quantity})"
#         elif self.service:
#             return f"{self.service.title} ({self.quantity})"
#         return f"Order Item #{self.id}"