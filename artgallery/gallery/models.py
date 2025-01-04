from django.db import models
from django.contrib.auth.models import User





class ArtPiece(models.Model):
    title = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='artpieces/')  

    def __str__(self):
        return self.title
    
class Order(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)  # Link to logged-in user
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    art_piece = models.ForeignKey(ArtPiece, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.art_piece.title} (Order {self.order.id})"




class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    is_artist = models.BooleanField(default=False)
    
    # Fields for artists
    # artist_name = models.CharField(max_length=255, null=True, blank=True)
    # short_bio = models.TextField(null=True, blank=True)
    # social_media_links = models.URLField(null=True, blank=True)
    # website = models.URLField(null=True, blank=True)
    # portfolio = models.FileField(upload_to='portfolio/', null=True, blank=True)

    def __str__(self):
        return self.user.username

















































