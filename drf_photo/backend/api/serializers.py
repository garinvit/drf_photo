from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework import serializers
# from ..photo.models import Album, AlbumTags, Photo, PhotoTags
from photo.models import AlbumTags, Album, PhotoTags, Photo

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




class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = '__all__'#["id", "title", "description", "tags", "created_at"]
        extra_kwargs = {'author': {'required': False}}


class PhotoTagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoTags
        fields = '__all__'
        extra_kwargs = {'author': {'required': False}}


class PhotoSerializer(serializers.ModelSerializer):
    # image_url = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = '__all__'

    # def get_image_url(self, photo):
    #     request = self.context.get('request')
    #     image_url = photo.image.url
    #     return request.build_absolute_uri(image_url)
#
#
# class TagSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Tag
#         fields = '__all__'
#
#
# class GeneralSerializer(serializers.ModelSerializer):
#     ingredientinfo_set = IngredientSerializer(many=True)
#     tags = TagSerializer(many=True)
#     class Meta:
#         model = Pizza
#         fields = '__all__'
#
#
# class PizzaSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Pizza
#         fields = '__all__'
