from django.contrib.auth import get_user_model
from rest_framework import serializers
from photo.models import Tags, Album, Photo
from app.utils import query_debugger  # noqa

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = UserModel.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )
        return user

    class Meta:
        model = UserModel
        fields = ("id", "username", "password",)


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = '__all__'


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'
        read_only_fields = ['created_at', ]
        extra_kwargs = {'album': {'required': True}}


class AlbumSerializer(serializers.ModelSerializer):
    # tags = TagsSerializer(many=True, required=False)
    photo_count = serializers.IntegerField(required=False, read_only=True)
    # photo_set = PhotoSerializer(many=True, required=False)

    # @query_debugger
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.context.get("view").action == "list":
            photos = instance.photo_set.all()
            representation['photo_set'] = [{x.id: x.title} for x in photos]
            representation['tags'] = instance.tags.values_list('title', flat=True)
        else:
            photos = instance.photo_set.all()
            serializer = PhotoSerializer(photos, many=True, context={"request": self.context.get("request")})
            representation['photo_set'] = serializer.data
            tags = TagsSerializer(instance.tags.all(), many=True, context={"request": self.context.get("request")})
            representation['tags'] = tags.data
        return representation

    class Meta:
        model = Album
        fields = ("id", "title", "author", "description", "created_at", "tags", "photo_count", "photo_set")
        read_only_fields = ['created_at', 'photo_count', "photo_set"]
        extra_kwargs = {
            'author': {'required': False},
        }
