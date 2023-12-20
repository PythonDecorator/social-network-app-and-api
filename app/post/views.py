"""
Views for the recipe APIs
"""
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from rest_framework import (viewsets, status, mixins)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django import views
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from core.models import Post, HashTag, Tag, Like, Comment  # noqa
from post import serializers  # noqa
from .forms import PostCreateForm, PostUpdateForm


# WEB PAGE POST VIEWS
class IndexListView(LoginRequiredMixin, views.generic.ListView):
    """Home page."""
    queryset = Post.objects.all()
    template_name = "home/content.html"
    context_object_name = "posts"

    def get_queryset(self):
        """Retrieve posts for authenticated user."""
        queryset = self.queryset

        return queryset.all()

    def get_context_data(self, **kwargs):
        context = super(IndexListView, self).get_context_data(**kwargs)
        posts = self.get_queryset().filter(user=self.request.user)

        liked = []
        for post in posts:
            if post.likes.filter(user=self.request.user).exists():
                liked.append(post.id)

        context['liked'] = liked

        return context


class CreatePostView(LoginRequiredMixin, views.generic.CreateView):
    """User registration view."""
    model = Post
    form_class = PostCreateForm
    template_name = 'home/post-create.html'

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)  # noqa
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('post:index')


class UpdatePostView(LoginRequiredMixin, views.generic.UpdateView):
    """Views for the profile page."""
    model = Post
    form_class = PostUpdateForm
    template_name = 'home/post-update.html'

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)  # noqa
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('post:index')

    def get_object(self, **kwargs):
        """Get the object specific to the user."""
        pk = self.kwargs.get("pk", None)

        if pk is None:
            raise Http404
        return get_object_or_404(Post, id=pk, user=self.request.user)

    def get_context_data(self, **kwargs):
        """Set the form values before rendering on the page"""
        context = super().get_context_data(**kwargs)
        post = self.get_object()

        data = {
            'title': post.title,
            'body': post.body,
            'img': post.img,
        }

        form = self.form_class(initial=data, user=post.user)

        context['form'] = form

        return context


@login_required
def comment_post(request):
    """Like a post."""
    if request.method == 'POST' and request.user.is_authenticated:
        pk = request.POST.get("post_id")
        body = request.POST.get("body")
        post = get_object_or_404(Post, pk=pk)

        if post:
            Comment.objects.create(user=request.user, post=post, body=body)
            post.save()
            comment = post.comments.filter(user=request.user).first()
            return JsonResponse({'success': True, 'comment_body': comment.body,
                                 "created_at": comment.created_at})

    return JsonResponse({}, status=400)


@login_required
def comment_post_update(request):
    """Like a post."""
    if request.method == 'POST' and request.user.is_authenticated:
        pk = request.POST.get("comment_id")
        body = request.POST.get("body")
        comment = get_object_or_404(Comment, user=request.user, pk=pk)

        if comment:
            comment.body = body
            comment.save()

            return JsonResponse({'success': True, 'comment_body': comment.body,
                                 "updated_at": comment.updated_at})

    return JsonResponse({}, status=400)


@login_required
def comment_post_delete(request):
    """Delete comment from a post."""
    if request.method == 'POST' and request.user.is_authenticated:
        pk = request.POST.get("comment_id")
        comment = get_object_or_404(Comment, user=request.user, pk=pk)

        if comment:
            comment.delete()

            return JsonResponse({'success': True, 'message': "Comment was deleted successfully."})

    return JsonResponse({}, status=400)


@login_required
def like_post(request):
    """Like a post."""
    if request.method == 'POST' and request.user.is_authenticated:
        pk = request.POST.get("post_id")
        post = get_object_or_404(Post, pk=pk)

        if not post.likes.filter(user=request.user).exists():
            Like.objects.create(user=request.user, post=post)
            post.likes_count += 1
            post.save()

            return JsonResponse({'success': True, 'new_like_count': post.likes_count})
        else:
            Like.objects.filter(user=request.user, post=post).delete()
            post.likes_count -= 1
            post.save()

            return JsonResponse({'success': True, 'new_like_count': post.likes_count})

    return JsonResponse({}, status=400)


class DeletePostView(LoginRequiredMixin, views.generic.DeleteView):
    model = Post
    template_name = 'home/post-delete.html'

    def get_success_url(self):
        return reverse_lazy('post:index')

    def get_object(self, **kwargs):
        """Get the object specific to the user."""
        pk = self.kwargs.get("pk", None)

        if pk is None:
            raise Http404
        return get_object_or_404(Post, id=pk, user=self.request.user)


# API VIEWS
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'hashtags',
                OpenApiTypes.STR,
                description='Comma separated list of hashtag IDs to filter',
            ),
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma separated list of tags IDs to filter',
            ),
        ]
    )
)
class PostViewSet(viewsets.ModelViewSet):
    """View for managing post APIs."""
    serializer_class = serializers.PostSerializer
    queryset = Post.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convert a list of strings to integers."""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve posts for authenticated user."""
        hashtags = self.request.query_params.get('hashtags')
        queryset = self.queryset

        if hashtags:
            hashtags_ids = self._params_to_ints(hashtags)
            queryset = queryset.filter(hashtags__id__in=hashtags_ids)

        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.PostSerializer
        elif self.action == 'upload_image':
            return serializers.PostImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new post."""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to post."""
        post = self.get_object()
        serializer = self.get_serializer(post, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by items assigned posts.',
            ),
        ]
    )
)
class BasePostAttrViewSet(mixins.DestroyModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """Base viewset for post attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset

        if assigned_only:
            queryset = queryset.filter(post__isnull=False)

        return queryset.filter(
            user=self.request.user).order_by('-name').distinct()


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by items assigned posts.',
            ),
        ]
    )
)
class TagBasePostAttrViewSet(mixins.DestroyModelMixin,
                             mixins.UpdateModelMixin,
                             mixins.ListModelMixin,
                             viewsets.GenericViewSet):
    """Base viewset for post attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset

        if assigned_only:
            queryset = queryset.filter(post__isnull=False)

        return queryset.filter(
            user=self.request.user).order_by('-somebody').distinct()


class TagViewSet(TagBasePostAttrViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class HashTagViewSet(BasePostAttrViewSet):
    """Manage hashtags in the database."""
    serializer_class = serializers.HashTagSerializer
    queryset = HashTag.objects.all()
