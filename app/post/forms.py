"""
Forms for the Post views
"""

from django import forms
from core.models import Post, Tag, Comment # noqa
from django.contrib.auth import get_user_model


class PostCreateForm(forms.ModelForm):
    """Form to create post."""
    title = forms.CharField(widget=forms.TextInput(
        attrs={"placeholder": "Title", "class": "form-control"}))
    body = forms.Textarea()
    img = forms.ImageField()

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(PostCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Post
        fields = ['title', 'body', "img"]

    def save(self, commit=True):
        instance = super(PostCreateForm, self).save(commit=False)
        instance.user = self.user

        tags_in_post_title = [{"somebody": word[1:]} for word in instance.title.split(" ")
                              if word[0] == "@" and get_user_model().objects.filter(username=word[1:]).exists()]

        tags_in_post_body = [{"somebody": word[1:]} for word in instance.body.split(" ")
                             if word[0] == "@" and get_user_model().objects.filter(username=word[1:]).exists()]

        if commit:
            instance.save()

        post_tags = tags_in_post_title + tags_in_post_body

        try:
            tag_id = Tag.objects.all().order_by("-id")[0].id
        except IndexError:
            tag_id = 0

        if post_tags:
            for tag in post_tags:
                tag_obj, created = Tag.objects.get_or_create(
                    id=tag_id,
                    user=self.user,
                    **tag,
                )
                instance.tags.add(tag_obj)
                tag_id += 1

        return instance


class PostUpdateForm(PostCreateForm):
    """Form to create post."""


class CommentCreateForm(forms.ModelForm):
    """Form to create comment on a post."""
    body = forms.Textarea()

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(CommentCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Comment
        fields = ['body', "post"]

    def save(self, commit=True):
        instance = super(CommentCreateForm, self).save(commit=False)
        instance.user = self.user
        print(instance)
        if commit:
            instance.save()

        return instance
