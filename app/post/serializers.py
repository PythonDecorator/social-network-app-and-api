"""
Serializers for post APIs
"""
from rest_framework import serializers
from core.models import Post  # noqa


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post."""

    class Meta:
        model = Post
        fields = [
            'id', 'title', "body", 'img',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        """Create a post."""
        post = Post.objects.create(**validated_data)
        return post

    def update(self, instance, validated_data):
        """Update post."""
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
