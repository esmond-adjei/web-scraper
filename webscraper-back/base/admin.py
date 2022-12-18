from django.contrib import admin
from .models import Movie, UserMovie

# Register your models here.
admin.site.register(Movie)
admin.site.register(UserMovie)
