from django.contrib.auth import get_user_model
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .serializers import PhotoSerializer, AlbumSerializer, TagsSerializer, UserSerializer
from photo.models import Tags, Album, Photo
from app.utils import MultipartJsonParser
from app.utils import query_debugger  # noqa


class IsAuthor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.get_author() == request.user.id


class CreateUserView(CreateAPIView):
    model = get_user_model()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer


class AlbumViewSet(ModelViewSet):
    queryset = Album.objects.all()
    permission_classes = [IsAuthenticated, IsAuthor]
    serializer_class = AlbumSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    ordering_fields = ('id', 'created_at', 'title', 'photo_count')
    filter_fields = ('id', 'title', )
    search_fields = ('title', 'description', 'tags__title', )

    # @query_debugger
    def get_queryset(self):
        # На 26 фотографий дает 36 запросов в БД около 120 мс
        # queryset = Album.objects.filter(author=self.request.user) \
        #     .annotate(photo_count=models.Count("photo"))
        # return queryset
        return self.queryset.filter(author=self.request.user) \
            .prefetch_related("photo_set__tags", "tags")\
            .annotate(photo_count=models.Count("photo"))  # 4 запроса в БД, время получения ответа 60 мс

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PhotoViewSet(ModelViewSet):
    queryset = Photo.objects.all()
    permission_classes = [IsAuthenticated, IsAuthor]
    serializer_class = PhotoSerializer
    parser_classes = (MultipartJsonParser, JSONParser)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    ordering_fields = ('id', 'created_at', 'title')
    filter_fields = ('id', 'title', )
    search_fields = ('title', 'description', 'tags__title', )

    def is_valid_album(self, request, album_id):
        album_ids = Album.objects.filter(author=request.user).values_list('id', flat=True)
        if album_id not in album_ids:
            raise PermissionDenied({'message': 'Альбом не принадлежит вам'})

    def get_queryset(self):
        return self.queryset.filter(album__author=self.request.user).prefetch_related("tags")

    def create(self, request, *args, **kwargs):
        if request.data:
            photo = request.data.get('photos')
            files = request.data.getlist('media')[::-1]
            if len(files) != len(photo):
                raise ValidationError("Не совпадает количество файлов и записей")
        else:
            return Response({'Error': 'empty data'}, status=400)
        saved_photo = []
        for index, photo in enumerate(photo):
            photo.update({"image": files[index], "image_small": files[index]})
            self.is_valid_album(request, photo.get("album"))
            serializer = self.get_serializer(data=photo)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            saved_photo.append({"data": serializer.data, "errors": serializer.errors})
        headers = self.get_success_headers(serializer.data)
        return Response({"success created": saved_photo}, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        self.is_valid_album(request, request.data.get("album"))
        return super().update(request, partial=True, *args, **kwargs)


class TagsViewSet(ModelViewSet):
    queryset = Tags.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    serializer_class = TagsSerializer
