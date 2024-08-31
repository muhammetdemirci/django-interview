"""django_rest_jwt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import include, re_path, path
from django.contrib import admin
from authentication import views as auth_views
from task import views as task_views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="Django API",
      default_version='v1',
      description="Test description",
      contact=openapi.Contact(email="dev.demirci@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

urlpatterns += [
    re_path(r'^api/auth/register/', auth_views.RegistrationView.as_view(), name='register'),
    re_path(r'^api/auth/login/', auth_views.LoginView.as_view(), name='login'),
    path('api/tasks', task_views.TasksView.as_view()),
    path('api/tasks/<int:id>', task_views.TaskView.as_view()),
    path('api/admin/tasks', task_views.AdminTasksView.as_view()),
    path('api/admin/tasks/<int:id>', task_views.AdminTaskView.as_view()),
    re_path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
