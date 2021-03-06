from distutils.command.upload import upload
from email.policy import default
from django.db import models
from django.contrib.auth.models import User
from mapbox_location_field.models import LocationField,  AddressAutoHiddenField
from PIL import Image
from cloudinary.models import CloudinaryField

# Create your models here.
class Administrator(models.Model):
    """Model definition for Administrator."""

    # TODO: Define fields here
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_photo = CloudinaryField('image', blank=True)

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
    location = LocationField(map_attrs={"center": [36.74,  -1.39], "marker_color": "red"})
    occupants = models.IntegerField(default=1, blank=True)
    address = AddressAutoHiddenField() 

    class Meta:
        """Meta definition for Neighbourhood."""

        verbose_name = 'Neighbourhood'
        verbose_name_plural = 'Neighbourhoods'

    def __str__(self):
        """Unicode representation of Neighbourhood."""
        return self.name

class Member(models.Model):
    """Model definition for Member."""

    # TODO: Define fields here
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    neighbourhood = models.ForeignKey(Neighbourhood, on_delete=models.CASCADE)
    profile_photo = CloudinaryField('image',default='v1650350714/image/upload/default_cxaayp.jpg', blank=True)
    name = models.CharField(max_length=20)
    username = models.CharField(max_length=20)
    email = models.EmailField()
    bio = models.TextField(blank=True, null=True)
    home_location = LocationField(map_attrs={"center": [36.74,  -1.39], "marker_color": "red"})
    address = AddressAutoHiddenField() 
    joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta definition for Member."""

        verbose_name = 'Member'
        verbose_name_plural = 'Members'

    # # resizing images # 
    # def save(self, *args, **kwargs):
    #     super().save()

    #     img = Image.open(self.profile_photo.path)

    #     if img.height > 100 or img.width > 100:
    #         new_img = (100, 100)
    #         img.thumbnail(new_img)
    #         img.save(self.profile_photo.path)

    def __str__(self):
        """Unicode representation of Member."""
        return str(self.user.username)

class Business(models.Model):
    """Model definition for Business."""

    # TODO: Define fields here
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    neighbourhood = models.ForeignKey(Neighbourhood, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    location = LocationField(map_attrs={"center": [36.74,  -1.39], "marker_color": "red"})
    description = models.TextField()
    email = models.EmailField()
    address = AddressAutoHiddenField() 

    @classmethod
    def setCenterLocation(cls, long, lat):
        cls.location = LocationField(map_attrs={"center": [long, lat], "marker_color": "red"})
        
    class Meta:
        """Meta definition for Business."""

        verbose_name = 'Business'
        verbose_name_plural = 'Businesses'

    def __str__(self):
        """Unicode representation of Business."""
        return self.name

class Post(models.Model):
    """Model definition for Post."""

    # TODO: Define fields here
    poster = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    neighbourhood = models.ForeignKey(Neighbourhood, on_delete=models.CASCADE)
    body = models.TextField()
    posted = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta definition for Post."""

        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        ordering = ['-posted']

    def __str__(self):
        """Unicode representation of Post."""
        return self.body

SOCIAL_SERVICES = (
    ('bank','Bank'),
    ('fire','Fire Department'),
    ('police','Police Department'),
    ('hospital', 'HealthCare'),  
    ('school','School'),  
)

class SocialServices(models.Model):
    """Model definition for SocialServices."""

    # TODO: Define fields here
    neighbourhood = models.ForeignKey(Neighbourhood, on_delete=models.CASCADE)
    name = models.CharField(max_length = 30)
    category = models.CharField(max_length=30, choices=SOCIAL_SERVICES)
    hotline = models.IntegerField()
    location = LocationField(map_attrs={"center": [36.74,  -1.39], "marker_color": "red"})
    address = AddressAutoHiddenField() 
    
    class Meta:
        """Meta definition for SocialServices."""

        verbose_name = 'SocialServices'
        verbose_name_plural = 'SocialServiceses'

    def __str__(self):
        """Unicode representation of SocialServices."""
        return self.name
