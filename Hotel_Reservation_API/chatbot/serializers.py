from rest_framework import serializers
from .models import Query

class QuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = ['id', 'question', 'answer', 'timestamp']
        read_only_fields = ['answer', 'timestamp']

class QueryInputSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=500)