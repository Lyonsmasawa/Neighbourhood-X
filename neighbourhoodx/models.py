from distutils.command.upload import upload
from pyexpat import model
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
