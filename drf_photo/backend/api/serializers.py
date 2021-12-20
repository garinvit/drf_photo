from django.contrib.auth import get_user_model
from rest_framework import serializers
from photo.models import AlbumTags, Album, PhotoTags, Photo
from rest_framework.fields import CurrentUserDefault

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


class AlbumTagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlbumTags
        fields = '__all__'


class PhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Photo
        fields = '__all__'
        read_only_fields = ['created_at',]
        extra_kwargs = {'author': {'required': False}}


class AlbumSerializer(serializers.ModelSerializer):
    photo_set = PhotoSerializer(many=True, required=False)
    photo_count = serializers.SerializerMethodField('get_photo_count')

    def get_photo_count(self, obj):
        return obj.photo_set.count()

    class Meta:
        model = Album
        fields = '__all__'  #["id", "title", "author", "description", "created_at", "tags", "photo_count", "photo_set"]
        read_only_fields = ['created_at', 'photo_count']
        extra_kwargs = {
            'author': {'required': False},
        }


class PhotoTagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoTags
        fields = '__all__'

