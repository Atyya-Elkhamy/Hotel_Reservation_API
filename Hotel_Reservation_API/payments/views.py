from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from decimal import Decimal
from .models import Payment, PaymentSettings
from .serializers import PaymentSerializer, PaymentSettingsSerializer
from bookings.models import Booking

class PaymentListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.is_staff:
            payments = Payment.objects.all()
        else:
            payments = Payment.objects.filter(user=request.user)
        
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PaymentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        if payment.user != request.user and not request.user.is_staff:
            return Response({"error": "Not authorized to view this payment."}, status=status.HTTP_403_FORBIDDEN)

        serializer = PaymentSerializer(payment)
        return Response(serializer.data)

    def post(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)

        # Process payment
        if 'process_payment' in request.data:
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

        # Refund payment
        if 'refund_payment' in request.data:
            if payment.status != Payment.PaymentStatus.COMPLETED:
                return Response({"error": "Only completed payments can be refunded."}, status=400)

            try:
                payment.refund()
                return Response({"success": True, "message": "Payment refunded successfully."})
            except Exception as e:
                return Response({"error": f"Refund failed: {str(e)}"}, status=400)

        return Response({"error": "Invalid action."}, status=400)

class PaymentForReservationCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
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

            serializer = PaymentSerializer(payment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Booking.DoesNotExist:
            return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class PaymentSettingsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        settings = PaymentSettings.objects.first()
        if not settings:
            settings = PaymentSettings.objects.create()
        serializer = PaymentSettingsSerializer(settings)
        return Response(serializer.data)

    def put(self, request):
        settings = PaymentSettings.objects.first()
        if not settings:
            settings = PaymentSettings.objects.create()

        serializer = PaymentSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
