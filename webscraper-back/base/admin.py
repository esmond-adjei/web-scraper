from django.contrib import admin
from .models import Movie, UserMovie

# Register your models here.
# admin.site.register(Movie)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = Movie.DisplayFields
    search_fields = Movie.SearchFields
    list_filter = Movie.FilterFields

# admin.site.register(UserMovie)


@admin.register(UserMovie)
class UserMovieAdmin(admin.ModelAdmin):
    list_display = UserMovie.DisplayFields
    list_filter = UserMovie.FilterFields
