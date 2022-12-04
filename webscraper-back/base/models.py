from django.db import models
# from django.forms import CharField, ImageField

# Create your models here.


class User(models.Model):
    username = models.CharField(max_length=100)


class MovieData(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.CharField(max_length=100)
    movie = models.CharField(max_length=256)
    movielink = models.CharField(max_length=2000, null=True, blank=True)
    imagelink = models.ImageField(upload_to='images', blank=True)
