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

# API ROUTE
urlpatterns = [
    path('api/post/', include(router.urls)),
]

# WEB PAGE ROUTE
urlpatterns += [
    path('', views.IndexListView.as_view(), name='index'),
    path('post/create/', views.CreatePostView.as_view(), name='create'),
    path('post/update/<int:pk>', views.UpdatePostView.as_view(), name='update'),
    path('post/delete/<int:pk>', views.DeletePostView.as_view(), name='delete'),
    path('post/like-post/', views.like_post, name='like-post'),
    path('post/comment-post/', views.comment_post, name='comment-post'),
    path('post/comment-post-update/', views.comment_post_update, name='comment-post-update'),
    path('post/comment-post-delete/', views.comment_post_delete, name='comment-post-delete'),
]
