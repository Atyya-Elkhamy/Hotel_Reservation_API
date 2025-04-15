# from django.shortcuts import render
# from django.http import JsonResponse
# from django.views import View
# from django.views.generic.edit import CreateView, UpdateView, DeleteView
# from django.views.generic.list import ListView
# from django.urls import reverse_lazy
# from .models import Booking
# from .serializers import BookingSerializer
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status

# class BookingListView(ListView):
#     model = Booking
#     template_name = 'bookings/booking_list.html'
#     context_object_name = 'bookings'

#     def get_queryset(self):
#         return Booking.objects.all()
# class BookingCreateView(CreateView):
#     model = Booking
#     template_name = 'bookings/booking_form.html'
#     fields = ['customer_name', 'room_number', 'check_in_date', 'check_out_date']
#     success_url = reverse_lazy('booking-list')

#     def form_valid(self, form):
#         return super().form_valid(form)
# class BookingUpdateView(UpdateView):
#     model = Booking
#     template_name = 'bookings/booking_form.html'
#     fields = ['customer_name', 'room_number', 'check_in_date', 'check_out_date']
#     success_url = reverse_lazy('booking-list')

#     def form_valid(self, form):
#         return super().form_valid(form)
# class BookingDeleteView(DeleteView):
#     model = Booking
#     template_name = 'bookings/booking_confirm_delete.html'
#     success_url = reverse_lazy('booking-list')

#     def delete(self, request, *args, **kwargs):
#         booking = self.get_object()
#         booking.delete()
#         return JsonResponse({'success': True})
# class BookingDetailView(View):
#     def get(self, request, *args, **kwargs):
#         booking_id = kwargs.get('pk')
#         booking = Booking.objects.get(id=booking_id)
#         return JsonResponse({
#             'customer_name': booking.customer_name,
#             'room_number': booking.room_number,
#             'check_in_date': booking.check_in_date,
#             'check_out_date': booking.check_out_date
#         })
#     def post(self, request, *args, **kwargs):
#         booking_id = kwargs.get('pk')
#         booking = Booking.objects.get(id=booking_id)
#         booking.customer_name = request.POST.get('customer_name')
#         booking.room_number = request.POST.get('room_number')
#         booking.check_in_date = request.POST.get('check_in_date')
#         booking.check_out_date = request.POST.get('check_out_date')
#         booking.save()
#         return JsonResponse({'success': True})
# class BookingSearchView(View):
#     def get(self, request):
#         query = request.GET.get('q')
#         bookings = Booking.objects.filter(customer_name__icontains=query)
#         results = [{'id': booking.id, 'customer_name': booking.customer_name} for booking in bookings]
#         return JsonResponse(results, safe=False)
# class BookingFilterView(View):
#     def get(self, request):
#         check_in_date = request.GET.get('check_in_date')
#         check_out_date = request.GET.get('check_out_date')
#         bookings = Booking.objects.filter(check_in_date__gte=check_in_date, check_out_date__lte=check_out_date)
#         results = [{'id': booking.id, 'customer_name': booking.customer_name} for booking in bookings]
#         return JsonResponse(results, safe=False)
# class BookingSortView(View):
#     def get(self, request):
#         sort_by = request.GET.get('sort_by')
#         bookings = Booking.objects.all().order_by(sort_by)
#         results = [{'id': booking.id, 'customer_name': booking.customer_name} for booking in bookings]
#         return JsonResponse(results, safe=False)
# class BookingPaginationView(View):
#     def get(self, request):
#         page = int(request.GET.get('page', 1))
#         per_page = int(request.GET.get('per_page', 10))
#         bookings = Booking.objects.all()[(page-1)*per_page:page*per_page]
#         results = [{'id': booking.id, 'customer_name': booking.customer_name} for booking in bookings]
#         return JsonResponse(results, safe=False)
# class BookingExportView(View):
#     def get(self, request):
#         bookings = Booking.objects.all()
#         # Export logic here (e.g., CSV, Excel)
#         return JsonResponse({'success': True})
# class BookingImportView(View):
#     def post(self, request):
#         # Import logic here (e.g., from CSV, Excel)
#         return JsonResponse({'success': True})
# class BookingEmailView(View):
#     def post(self, request):
#         booking_id = request.POST.get('booking_id')
#         booking = Booking.objects.get(id=booking_id)
#         # Email logic here
#         return JsonResponse({'success': True})

#     class BookingListAPIView(APIView):
#         def get(self, request):
#             bookings = Booking.objects.all()
#             serializer = BookingSerializer(bookings, many=True)
#             return Response(serializer.data)

#     class BookingCreateAPIView(APIView):
#         def post(self, request):
#             serializer = BookingSerializer(data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     class BookingDetailAPIView(APIView):
#         def get(self, request, pk):
#             try:
#                 booking = Booking.objects.get(pk=pk)
#             except Booking.DoesNotExist:
#                 return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
#             serializer = BookingSerializer(booking)
#             return Response(serializer.data)

#         def put(self, request, pk):
#             try:
#                 booking = Booking.objects.get(pk=pk)
#             except Booking.DoesNotExist:
#                 return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
#             serializer = BookingSerializer(booking, data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         def delete(self, request, pk):
#             try:
#                 booking = Booking.objects.get(pk=pk)
#             except Booking.DoesNotExist:
#                 return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
#             booking.delete()
#             return Response({'success': True}, status=status.HTTP_204_NO_CONTENT)