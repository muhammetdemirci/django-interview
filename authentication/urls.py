from django.urls import include, re_path


from authentication import views

urlpatterns = [
    re_path(r'^register/', views.RegistrationView.as_view(), name='register'),
    re_path(r'^login/', views.LoginView.as_view(), name='login')
]
