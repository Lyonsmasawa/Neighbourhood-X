from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Administrator(models.Model):
    """Model definition for Administrator."""

    # TODO: Define fields here
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_photo = models.ImageField(upload_to = 'images')

    class Meta:
        """Meta definition for Administrator."""

        verbose_name = 'Administrator'
        verbose_name_plural = 'Administrators'

    def __str__(self):
        """Unicode representation of Administrator."""
        return str(self.user.username)

class Neighbourhood(models.Model):
    """Model definition for Neighbourhood."""

    # TODO: Define fields here
    admin = models.ForeignKey(Administrator, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    location = models.CharField(max_length=30)
    occupants = models.IntegerField(default=1)

    class Meta:
        """Meta definition for Neighbourhood."""

        verbose_name = 'Neighbourhood'
        verbose_name_plural = 'Neighbourhoods'

    def __str__(self):
        """Unicode representation of Neighbourhood."""
        pass
