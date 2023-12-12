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
router.register('tags', views.TagViewSet)
router.register('hashtags', views.HashTagViewSet)

app_name = 'post'

urlpatterns = [

    path('', include(router.urls)),

]
