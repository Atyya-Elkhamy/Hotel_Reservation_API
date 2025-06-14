from django.db import models
from accounts.models import User

# Create your models here.

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications" ,null=True, blank=True)
    message = models.TextField(max_length=500)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"
    class Meta():
        db_table = "notifications"

