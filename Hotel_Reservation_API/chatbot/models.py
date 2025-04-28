from django.db import models


class Query(models.Model):
    MODEL_CHOICES = [
        ('gemini', 'Gemini 1.5 Pro'),
        ('ollama', 'Ollama Llama3'),
    ]

    question = models.CharField(max_length=500)
    answer = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    # New fields to track model information
    model_requested = models.CharField(max_length=20, choices=MODEL_CHOICES, default='gemini')
    model_used = models.CharField(max_length=20, choices=MODEL_CHOICES, default='gemini')
    fallback_used = models.BooleanField(default=False)

    def __str__(self):
        return self.question