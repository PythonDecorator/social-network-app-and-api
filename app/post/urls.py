"""
URL mappings for the post app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from post import views  # noqa

router = DefaultRouter()
router.register('posts', views.PostViewSet)

app_name = 'post'

urlpatterns = [

    path('', include(router.urls)),

]
