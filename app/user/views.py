"""
Views for the Users
"""
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
# from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from user.serializers import UserSerializer, AuthTokenSerializer  # noqa

from django import views
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse

from .forms import SignUpForm, LoginForm, EditProfileForm
from core.models import Follower  # noqa


class RegisterUserView(SuccessMessageMixin, views.generic.CreateView):
    """User registration view."""
    model = get_user_model()
    form_class = SignUpForm
    success_url = reverse_lazy('user:login')
    template_name = 'authentication/signup.html'
    success_message = "Your account was created successfully"


class LoginUserView(views.generic.View):
    template_name = 'authentication/login.html'
    form_class = LoginForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, context={'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():

            _user = get_user_model().objects.filter(email=form.cleaned_data['email']).first()

            if _user:
                user = authenticate(
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=_user.first_name,
                    last_name=_user.last_name,
                    username=_user.username,
                )

                if user is not None:
                    login(request, user)
                    return redirect('post:index')

                msg = 'Please check your password and try again.'
                messages.error(request, msg)

                return render(request, self.template_name, context={'form': form})

            msg = 'That email does not exist. Please signup instead.'
            messages.error(request, msg)
        return render(request, self.template_name, context={'form': form})


class ProfileView(LoginRequiredMixin, views.generic.DetailView):
    """Views for the post page."""
    model = get_user_model()
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = "home/profile.html"

    def get(self, request, *args, **kwargs):
        object1 = super(ProfileView, self).get(request, *args, **kwargs)
        username = kwargs.get("username")
        user = self.request.user.username
        if username != user:
            raise Http404

        return object1


class ProfileUpdateView(LoginRequiredMixin, views.generic.UpdateView):
    """Views for the profile page."""
    model = get_user_model()
    slug_url_kwarg = "username"
    slug_field = "username"

    form_class = EditProfileForm
    template_name = 'home/profile-update.html'

    def get_success_url(self):
        return reverse('user:profile', kwargs={'username': self.get_object().username})


#     def get_object(self, **kwargs):
#         """Get the object specific to the user."""
#         email = self.kwargs.get("email")
#         if email is None:
#             raise Http404
#         return get_object_or_404(get_user_model(), user__email__iexact=email)
#
#     def get_context_data(self, **kwargs):
#         """Set the form values before rendering on the page"""
#         context = super().get_context_data(**kwargs)
#         user = self.get_object()
#
#         data = {
#             'First Name': user.first_name,
#             'Last Name': user.last_name,
#         }
#
#         form = self.form_class(initial=data, instance=user.user)
#
#         context['form'] = form
#         return context

# @login_required
# def follow_view(request, username):
#
#     followee = get_object_or_404(get_user_model(), username=username)
#     # check if the current user is already following the user
#     if Follower.objects.filter(follower=request.user, followee=followee).exists():
#         # if yes, show a message that they are already following
#         messages.info(request, f"You are already following {followee.username}.")
#     else:
#         # if no, create a new follow object and save it to the database
#         follow = Follow(follower=request.user, followee=followee)
#         follow.save()
#         # show a message that they have successfully followed the user
#         messages.success(request, f"You have followed {followee.username}.")
#     # redirect to the user's profile page
#     return redirect('profile',
#                     username=username)  # assuming you have a url pattern named 'profile'
#                     that takes a username as an argument

@login_required
def follow(request):
    """Follow a user."""
    if request.method == 'POST' and request.user.is_authenticated:
        leader_id = request.POST.get("leader_id")
        user_to_follow = get_object_or_404(get_user_model(), id=leader_id)

        if user_to_follow == request.user:
            return JsonResponse({'error': 'Cannot follow yourself.'}, status=400)

        followed = Follower.objects.filter(follower=request.user, leader=user_to_follow).exists()

        if followed:
            return JsonResponse({'error': 'Already following this user.'}, status=400)

        follower = Follower(follower=request.user, leader=user_to_follow)
        follower.save()

        return JsonResponse({'success': True, "message": f"You have followed @{user_to_follow.username}"})

    return JsonResponse({}, status=400)


# API
class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Mange the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user
