from django.db import models

class Query(models.Model):
    question = models.CharField(max_length=500)
    answer = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question