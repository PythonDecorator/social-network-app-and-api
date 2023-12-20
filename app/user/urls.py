"""
URL mappings for the user API.
"""
from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from user import views  # noqa

app_name = 'user'

# API ROUTE
urlpatterns = [
    path('api/user/create/', views.CreateUserView.as_view(), name='create'),
    path('api/user/token/', views.CreateTokenView.as_view(), name='token'),
    path('api/user/me/', views.ManageUserView.as_view(), name='me'),
]

# WEB PAGE ROUTE
urlpatterns += [
    path('signup/', views.RegisterUserView.as_view(), name="signup"),
    path('login/', views.LoginUserView.as_view(), name="login"),
    path("logout/", login_required(LogoutView.as_view(template_name="authentication/logout.html")),
         name="logout"),
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile'),
    path('profile/<str:username>/update/', views.ProfileUpdateView.as_view(),
         name='profile-update'),
]
