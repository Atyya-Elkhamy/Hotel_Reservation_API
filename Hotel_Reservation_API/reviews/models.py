from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User
from hotels.models import Hotel

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating must be between 1 and 5"
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review {self.id} - {self.hotel.name}"

    class Meta:
        db_table = "reviews"
        ordering = ['-created_at']
        unique_together = ['user', 'hotel']