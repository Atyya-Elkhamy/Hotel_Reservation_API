from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from decimal import Decimal
from .models import Payment, PaymentSettings
from .serializers import PaymentSerializer, ClientInfoSerializer, PaymentMethodSerializer
from bookings.models import Booking
import time

class ClientInfoPaymentTypeView(APIView):
    """
    First view: Collects client information and payment type selection
    """
    # permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        print ("requ.user" , request.user.id)
        print(request.data)
        booking_id = request.data.get('booking_id')
        if not booking_id:
            return Response({"error": "Booking ID is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            booking = Booking.objects.get(id=booking_id)
         
            # if booking.id != request.user.id:
               
            #     return Response({"error": "Not authorized to pay for this booking"}, status=status.HTTP_403_FORBIDDEN)
                
            serializer = ClientInfoSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            print("serializer.validated_data", serializer.validated_data)    
            payment_type = request.data.get('payment_type')
            if payment_type not in ['cash', 'online']:
                return Response({"error": "Invalid payment type. Choose 'cash' or 'online'"}, 
                            status=status.HTTP_400_BAD_REQUEST)
            
            if not booking.items.exists():
                return Response({"error": "No rooms in this booking"}, status=status.HTTP_400_BAD_REQUEST)
            
            from hotels.models import Room
            for item in booking.items.all():
                room = Room.objects.filter(hotel=booking.hotel, room_type=item.room_type).first()
                if not room:
                    return Response({"error": f"Room type {item.room_type} not found"}, 
                                  status=status.HTTP_400_BAD_REQUEST)
                if room.available_rooms < item.quantity:
                    return Response({"error": f"Not enough available rooms of type {item.room_type.room_type}. Only {room.available_rooms} left."}, 
                                  status=status.HTTP_400_BAD_REQUEST)
            
            if payment_type == 'cash':
                deposit_percent = 30
                amount = (Decimal(deposit_percent) / Decimal('100')) * booking.total_price
                is_deposit = True
            else:
                amount = booking.total_price
                is_deposit = False
            
            first_item = booking.items.first()
            first_room = Room.objects.get(hotel=booking.hotel, room_type=first_item.room_type)
            
            payment = Payment.objects.create(
                booking=booking,
                user=request.user,
                room=first_room,  
                hotel=booking.hotel,
                first_name=serializer.validated_data.get('first_name'),
                last_name=serializer.validated_data.get('last_name'),
                email=serializer.validated_data.get('email'),
                phone=serializer.validated_data.get('phone'),
                address=serializer.validated_data.get('address'),
                city=serializer.validated_data.get('city'),
                region=serializer.validated_data.get('region'),
                is_deposit=payment_type == 'cash',
                amount=amount,
                status=Payment.PaymentStatus.PENDING
            )
            
            if payment_type == 'online' or (payment_type == 'cash' and is_deposit):
                for item in booking.items.all():
                    room = Room.objects.get(hotel=booking.hotel, room_type=item.room_type)
                    room.available_rooms -= item.quantity
                    room.save()
                
                booking.status = 'confirmed'
                booking.save()
            
            response_data = {
                'payment_id': payment.id,
                'booking_summary': {
                    'booking_id': booking.id,
                    'rooms': [{'room_type': item.room_type.room_type, 'quantity': item.quantity} 
                            for item in booking.items.all()],
                    'check_in': booking.check_in,
                    'check_out': booking.check_out,
                    'total_price': float(booking.total_price),
                },
                'is_deposit': payment.is_deposit,
                'amount_to_pay': float(payment.amount),
                'next_step': 'payment_method_selection'
            }
        
            
            if payment.is_deposit:
                response_data['deposit_message'] = f"A 30% deposit of {float(payment.amount)} is required for cash payments."
                
            return Response(response_data, status=status.HTTP_201_CREATED)
        
            
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class PaymentMethodSelectionView(APIView):
    """
    Second view: Process payment method selection and complete payment
    """
    # permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        payment_id = request.data.get('payment_id')
        payment_method = request.data.get('payment_method')
        
        if not payment_id:
            return Response({"error": "Payment ID is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            payment = Payment.objects.get(id=payment_id)
            
            if payment.user.id != request.user.id and not request.user.is_staff:
                return Response({"error": "Not authorized to access this payment"}, 
                               status=status.HTTP_403_FORBIDDEN)
                
            if payment.status != Payment.PaymentStatus.PENDING:
                return Response({"error": "This payment has already been processed"}, 
                               status=status.HTTP_400_BAD_REQUEST)
                
            if payment_method not in [
                Payment.PaymentMethodChoice.CREDIT_CARD,
                Payment.PaymentMethodChoice.PAYPAL,
                Payment.PaymentMethodChoice.BANK_TRANSFER
            ]:
                return Response({"error": "Invalid payment method"}, status=status.HTTP_400_BAD_REQUEST)
                
            settings = PaymentSettings.objects.first()
            if not settings:
                settings = PaymentSettings()
                settings.save()
                
            allowed_methods = []
            if settings.allow_card_payment:
                allowed_methods.append(Payment.PaymentMethodChoice.CREDIT_CARD)
            if settings.allow_paypal:
                allowed_methods.append(Payment.PaymentMethodChoice.PAYPAL)
            if settings.allow_bank_transfer:
                allowed_methods.append(Payment.PaymentMethodChoice.BANK_TRANSFER)
                
            if payment_method not in allowed_methods:
                return Response({"error": "This payment method is not allowed"}, 
                               status=status.HTTP_400_BAD_REQUEST)
                
            payment.payment_method = payment_method
            payment.save()
            
            # Here we would typically integrate with a payment gateway
            # This is just a simulation for now
            try:
                transaction_id = f"TRANS-{payment.id}-{payment.booking.id}"
                payment.mark_as_completed(transaction_id)
                booking = payment.booking
                
                booking = payment.booking
                if payment.is_deposit:
                    booking.deposit_paid = True
                else:
                    booking.is_paid = True
                booking.save()
                
                return Response({
                    "success": True,
                    "message": "Payment processed successfully",
                    "transaction_id": transaction_id,
                    "amount_paid": float(payment.amount),
                    "is_deposit": payment.is_deposit,
                    "remaining_amount": float(booking.total_price - payment.amount) if payment.is_deposit else 0
                })
                
            except Exception as e:
                payment.status = Payment.PaymentStatus.PENDING
                payment.save()
                return Response({"error": f"Payment processing failed: {str(e)}"}, 
                               status=status.HTTP_400_BAD_REQUEST)
                
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
