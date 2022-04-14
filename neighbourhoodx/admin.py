from django.contrib import admin
from .models import Administrator, Business, Member, Neighbourhood, Post, SocialServices

# Register your models here.
admin.site.register(Administrator)
admin.site.register(Neighbourhood)
admin.site.register(Member)
admin.site.register(Business)
admin.site.register(Post)
admin.site.register(SocialServices)
