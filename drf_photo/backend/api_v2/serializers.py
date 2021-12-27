from django.contrib.auth import get_user_model
from rest_framework import serializers
from photo.models import Tags, Album, Photo

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
    photo_count = serializers.SerializerMethodField('get_photo_count')

    def get_photo_count(self, obj):
        return obj.photo_set.count()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.context.get("photo_set", "") != "false":
            photos = instance.get_photo_from_album()
            serializer = PhotoSerializer(photos, many=True, context={"request": self.context.get("request")})
            serializer = serializer.data
            representation['photos'] = serializer
        if self.context.get("display_tags", "").lower() != "false":
            tags = instance.tags.all()
            serializer = TagsSerializer(tags, many=True, required=False)
            serializer = serializer.data
            representation['tags'] = serializer
        else:
            representation.pop('tags')
        # print(representation)
        return representation

    class Meta:
        model = Album
        fields = '__all__'  # ["id", "title", "author", "description", "created_at", "tags", "photo_count", "photo_set"]
        read_only_fields = ['created_at', 'photo_count']
        extra_kwargs = {
            'author': {'required': False},
        }
