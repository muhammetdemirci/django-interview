from django.urls import include, re_path

from task import views

urlpatterns = [
    re_path(r'^', views.TasksView.as_view(), name='tasks'),
]
