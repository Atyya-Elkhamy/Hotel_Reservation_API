from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Review
from .serializers import ReviewSerializer


class ReviewListCreateAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        print('User making GET request:', request.user) 
        reviews = Review.objects.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "You must be logged in to create a review."},
                            status=status.HTTP_401_UNAUTHORIZED)
        serializer = ReviewSerializer(data=request.data, context={'request': request})
        print(request)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewDetailAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return None

    def get(self, request, pk, format=None):
        review = self.get_object(pk)
        if not review:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ReviewSerializer(review, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        review = self.get_object(pk)
        if not review:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if review.user != request.user:
            return Response({"error": "You can only edit your own reviews"},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = ReviewSerializer(review, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        review = self.get_object(pk)
        if not review:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if review.user != request.user:
            return Response({"error": "You can only delete your own reviews"},
                            status=status.HTTP_403_FORBIDDEN)

        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class HotelReviewsAPIView(APIView):
    def get(self, request, hotel_id, format=None):
        reviews = Review.objects.filter(hotel_id=hotel_id)
        serializer = ReviewSerializer(reviews, many=True, context={'request': request})
        return Response(serializer.data)
