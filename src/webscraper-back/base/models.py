from django.db import models
from django.forms import CharField, ImageField

# Create your models here.
class MovieData(models.Model):
    query = models.CharField(max_length=100)
    movie = models.CharField(max_length=256)
    movielink = models.CharField(max_length=2000)
    imagelink = models.ImageField(upload_to='images', blank=True)
