from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Administrator(models.Model):
    """Model definition for Administrator."""

    # TODO: Define fields here
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_photo = models.ImageField()

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

class Member(models.Model):
    """Model definition for Member."""

    # TODO: Define fields here
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    neighbourhood = models.ForeignKey(Neighbourhood, on_delete=models.CASCADE)
    profile_photo = models.ImageField()


    class Meta:
        """Meta definition for Member."""

        verbose_name = 'Member'
        verbose_name_plural = 'Members'

    def __str__(self):
        """Unicode representation of Member."""
        pass

class Business(models.Model):
    """Model definition for Business."""

    # TODO: Define fields here
    

    class Meta:
        """Meta definition for Business."""

        verbose_name = 'Business'
        verbose_name_plural = 'Businesss'

    def __str__(self):
        """Unicode representation of Business."""
        pass
