from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Query
from .serializers import QuerySerializer, QueryInputSerializer
from .chat_service import QAService
import logging

logger = logging.getLogger(__name__)


class QueryAPIView(APIView):
    def post(self, request):
        # Validate input
        serializer = QueryInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Get the question from request
        question = serializer.validated_data['question']

        try:
            # Initialize QA service and get answer
            qa_service = QAService()
            answer = qa_service.get_answer(question)

            # Save to database
            query = Query(question=question, answer=answer)
            query.save()

            # Return response
            response_serializer = QuerySerializer(query)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error in QueryAPIView: {str(e)}")
            return Response(
                {"error": "An error occurred while processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QueryHistoryAPIView(APIView):
    def get(self, request):
        queries = Query.objects.all().order_by('-timestamp')
        serializer = QuerySerializer(queries, many=True)
        return Response(serializer.data)
