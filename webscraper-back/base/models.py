from django.db import models
from django.contrib.auth.models import User
# from django.forms import CharField, ImageField

# Create your models here.


class Movie(models.Model):
    username = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    query = models.CharField(max_length=100)
    moviename = models.CharField(max_length=256, unique=True)
    movielink = models.TextField(null=True, blank=True)
    imagelink = models.CharField(max_length=2000, null=True, blank=True)
    datecreated = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.moviename
