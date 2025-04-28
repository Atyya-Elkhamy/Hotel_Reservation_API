from rest_framework import serializers
from .models import Query

class QuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = ['id', 'question', 'answer', 'timestamp', 'model_requested', 'model_used', 'fallback_used']
        read_only_fields = ['answer', 'timestamp', 'model_used', 'fallback_used']

class QueryInputSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=500)
    model = serializers.ChoiceField(choices=['gemini', 'ollama'], default='gemini', required=False)