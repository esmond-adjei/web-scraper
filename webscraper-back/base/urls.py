from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.registerPage, name='register'),
    path('login', views.loginPage, name='login'),
    path('login', LogoutView.as_view(next_page='login'), name='logout'),
    path('progress', views.progress, name='progress'),
    path('save', views.save, name='save'),
    path('select-movie/<str:moviename>', views.selectMovie, name='select-movie'),
]
