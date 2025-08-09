from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        """
        String representation of the UserProfile model.
        
        Returns:
            str: The username of the associated user
        """
        return self.user.username