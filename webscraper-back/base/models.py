from django.db import models
from django.contrib.auth.models import User
# from django.forms import CharField, ImageField

# Create your models here.


class Movie(models.Model):
    query = models.CharField(max_length=100)
    moviename = models.CharField(max_length=256, unique=True)
    movielink = models.TextField(null=True, blank=True)
    imagelink = models.CharField(max_length=500, null=True, blank=True)
    movie_type = models.CharField(max_length=50, null=True, blank=True)
    datecreated = models.DateTimeField(auto_now_add=True, blank=True)

    DisplayFields = ['moviename', 'movie_type', 'datecreated', 'imagelink']
    SearchFields = ['moviename', 'query']
    FilterFields = ['movie_type', 'query']

    def __str__(self):
        return self.moviename


class UserMovie(models.Model):
    user_movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    username = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    DisplayFields = ['user_movie', 'username']
    FilterFields = ['username']

    def __str__(self):
        return str(self.username) + '_' + self.user_movie.moviename
