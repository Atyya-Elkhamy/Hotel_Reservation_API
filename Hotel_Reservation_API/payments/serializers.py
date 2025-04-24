from rest_framework import serializers
from .models import Payment, PaymentSettings


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ['transaction_id', 'status', 'created_at']

    def validate(self, data):
        booking = data.get('booking')
        amount = data.get('amount')
        payment_method = data.get('payment_method')
        is_deposit = data.get('is_deposit')

        if booking and hasattr(booking, 'payment'):
            raise serializers.ValidationError({
                "booking": "This booking already has a payment."
            })
        
        if amount is not None and amount <= 0:
            raise serializers.ValidationError({
                "amount": "Amount must be greater than zero."
            })

        settings = PaymentSettings.objects.first()
        if settings:
            if payment_method == Payment.PaymentMethodChoice.CREDIT_CARD and not settings.allow_card_payment:
                raise serializers.ValidationError({
                    "payment_method": "Credit card payments are disabled."
                })
            if payment_method == Payment.PaymentMethodChoice.PAYPAL and not settings.allow_paypal:
                raise serializers.ValidationError({
                    "payment_method": "PayPal is currently disabled."
                })
            if payment_method == Payment.PaymentMethodChoice.BANK_TRANSFER and not settings.allow_bank_transfer:
                raise serializers.ValidationError({
                    "payment_method": "Bank transfers are not accepted."
                })

            # 4. Validate deposit amount if is_deposit is True
            if is_deposit:
                total_price = booking.total_price if booking else None
                expected_deposit = settings.calculate_deposit(total_price) if total_price else None
                if expected_deposit and amount != expected_deposit:
                    raise serializers.ValidationError({
                        "amount": f"Deposit should be exactly {expected_deposit} for this booking."
                    })

        return data


class PaymentSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentSettings
        fields = "__all__"


