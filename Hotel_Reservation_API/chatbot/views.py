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

        # Get the question and model choice from request
        question = serializer.validated_data['question']
        model_choice = serializer.validated_data.get('model', 'gemini')

        try:
            # Initialize QA service and get answer with model choice
            qa_service = QAService()
            result = qa_service.get_answer_with_model_choice(question, model=model_choice)

            # Save to database with model information
            query = Query(
                question=question,
                answer=result['answer'],
                model_requested=model_choice,
                model_used=result['model_used'],
                fallback_used=result['fallback_used']
            )
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
        # Get optional model filter
        model_filter = request.query_params.get('model', None)

        if model_filter:
            queries = Query.objects.filter(model_used=model_filter).order_by('-timestamp')
        else:
            queries = Query.objects.all().order_by('-timestamp')

        serializer = QuerySerializer(queries, many=True)
        return Response(serializer.data)