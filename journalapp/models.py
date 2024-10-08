from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class entry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the User model
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically store creation time
    isEdited = models.BooleanField(default=False)  # Initially not edited
    edited_at = models.DateTimeField(null=True, blank=True)
    emotion = models.TextField()
