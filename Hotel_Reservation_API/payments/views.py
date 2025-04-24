# payments/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from decimal import Decimal

from .models import Payment, PaymentSettings
from .serializers import PaymentSerializer, PaymentSettingsSerializer
from bookings.models import Booking   

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        payment = self.get_object()

        if payment.status != Payment.PaymentStatus.PENDING:
            return Response({"error": "Payment is not in a pending state."}, status=400)

        try:
            transaction_id = f"TRANS-{payment.id}-{payment.booking.id}"
            payment.mark_as_completed(transaction_id)

            booking = payment.booking
            if payment.is_deposit:
                booking.deposit_paid = True
            else:
                booking.is_paid = True
            booking.save()

            return Response({
                "success": True,
                "message": "Payment processed successfully.",
                "transaction_id": transaction_id
            })
        except Exception as e:
            payment.mark_as_failed()
            return Response({"error": f"Payment failed: {str(e)}"}, status=400)

    @action(detail=True, methods=['post'])
    def refund_payment(self, request, pk=None):
        payment = self.get_object()

        if payment.status != Payment.PaymentStatus.COMPLETED:
            return Response({"error": "Only completed payments can be refunded."}, status=400)

        try:
            payment.refund()
            return Response({"success": True, "message": "Payment refunded successfully."})
        except Exception as e:
            return Response({"error": f"Refund failed: {str(e)}"}, status=400)

    @action(detail=False, methods=['post'])
    def create_payment_for_reservation(self, request):
        reservation_id = request.data.get('reservation_id')
        payment_method = request.data.get('payment_method')  # string value from choices
        is_deposit = request.data.get('is_deposit', False)

        try:
            reservation = Booking.objects.get(id=reservation_id)

            if reservation.guest.id != request.user.id and not request.user.is_staff:
                return Response({"error": "Not authorized to pay for this booking."}, status=403)

            settings = PaymentSettings.objects.first()
            if not settings:
                return Response({"error": "Payment settings not configured."}, status=400)

            allowed_methods = []
            if settings.allow_card_payment:
                allowed_methods.append(Payment.PaymentMethodChoice.CREDIT_CARD)
            if settings.allow_paypal:
                allowed_methods.append(Payment.PaymentMethodChoice.PAYPAL)
            if settings.allow_bank_transfer:
                allowed_methods.append(Payment.PaymentMethodChoice.BANK_TRANSFER)

            if payment_method not in allowed_methods:
                return Response({"error": "This payment method is not allowed."}, status=400)

            amount = settings.calculate_deposit(reservation.total_price) if is_deposit else reservation.total_price

            payment = Payment.objects.create(
                booking=reservation,
                user=request.user,
                amount=amount,
                payment_method=payment_method,
                is_deposit=is_deposit
            )

            serializer = self.get_serializer(payment)
            return Response(serializer.data, status=201)

        except Booking.DoesNotExist:
            return Response({"error": "Booking not found."}, status=404)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=400)


class PaymentSettingsViewSet(viewsets.ModelViewSet):
    queryset = PaymentSettings.objects.all()
    serializer_class = PaymentSettingsSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_object(self):
        settings = PaymentSettings.objects.first()
        if not settings:
            settings = PaymentSettings.objects.create()
        return settings
