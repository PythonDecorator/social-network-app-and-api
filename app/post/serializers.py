"""
Serializers for post APIs
"""
from rest_framework import serializers
from core.models import User, Post, HashTag, Tag  # noqa
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'somebody']
        read_only_fields = ['id']

    def validate(self, attrs):
        """Validate tags."""
        somebody = attrs.get('somebody')
        if somebody[0] != "@":
            msg = _('Please add " @" before all the tags.')
            raise serializers.ValidationError(msg, code='@Before tags')

        attrs['somebody'] = somebody
        return attrs


class HashTagSerializer(serializers.ModelSerializer):
    """Serializer for Hashtags."""

    class Meta:
        model = HashTag
        fields = ['id', 'name']
        read_only_fields = ['id']


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post."""
    hashtags = HashTagSerializer(many=True, required=False)
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = [
            'id', 'title', "body", 'img', "hashtags", "tags"
        ]
        read_only_fields = ['id']

    @staticmethod
    def _get_tags_from_post_and_validate(body: str, tags: list) -> list:
        """Return a list of tags from the post."""
        words: list = body.split(" ")

        # Add the tags created in for and post body.
        all_tags = [word[1:] for word in words if word[0] == "@"] + \
                   [tag['somebody'][1:] for tag in tags]

        validated_tags = []

        for username in all_tags:
            if get_user_model().objects.filter(username=username).exists():
                validated_tags.append({"somebody": username})

        return validated_tags

    def _get_or_create_tags(self, tags, post):
        """Handle getting or creating tags as needed."""
        tags = self._get_tags_from_post_and_validate(post.body, tags)
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            post.tags.add(tag_obj)

    def _get_or_create_hashtags(self, hashtags, post):
        """Handle getting or creating hashtags as needed."""
        auth_user = self.context['request'].user
        for hashtag in hashtags:
            hashtag_obj, created = HashTag.objects.get_or_create(
                user=auth_user,
                **hashtag,
            )
            post.hashtags.add(hashtag_obj)

    def create(self, validated_data):
        """Create a post."""
        hashtags = validated_data.pop('hashtags', [])
        tags = validated_data.pop('tags', [])
        post = Post.objects.create(**validated_data)
        self._get_or_create_hashtags(hashtags, post)
        self._get_or_create_tags(tags, post)

        return post

    def update(self, instance, validated_data):
        """Update post."""
        hashtags = validated_data.pop('hashtags', None)
        tags = validated_data.pop('tags', None)

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        if hashtags is not None:
            instance.hashtags.clear()
            self._get_or_create_hashtags(hashtags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PostImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to posts."""

    class Meta:
        model = Post
        fields = ['id', 'img']
        read_only_fields = ['id']
        extra_kwargs = {'img': {'required': 'True'}}
