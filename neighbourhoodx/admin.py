from django.contrib import admin
from .models import Administrator, Business, Member, Neighbourhood, Post, SocialServices
from mapbox_location_field.admin import MapAdmin

# Register your models here.
admin.site.register(Administrator)
admin.site.register(Neighbourhood, MapAdmin)
admin.site.register(Member, MapAdmin)
admin.site.register(Business, MapAdmin)
admin.site.register(Post)
admin.site.register(SocialServices, MapAdmin)
