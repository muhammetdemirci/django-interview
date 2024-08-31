from django.urls import include, re_path

from home import views

urlpatterns = [
    re_path(r'^', views.HomeView.as_view(), name='home'),
]
