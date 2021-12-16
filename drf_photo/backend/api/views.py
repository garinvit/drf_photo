from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import permissions
from rest_framework.decorators import parser_classes
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import MultiPartParser, FileUploadParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, PhotoSerializer, AlbumSerializer, AlbumTagsSerializer, PhotoTagsSerializer
from photo.models import AlbumTags, Album, PhotoTags, Photo
import json

from .utils import MultipartJsonParser


class CreateUserView(CreateAPIView):
    model = get_user_model()
    permission_classes = (AllowAny, )
    serializer_class = UserSerializer


class CurrentUserView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response({
                'username': request.user.username,
            })
        return Response({
            'status': 'failed'
        }, status=401)

class AlbumModelView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        albums = Album.objects.filter(author=request.user.id)
        serializer = AlbumSerializer(albums, many=True)
        return Response({'albums': serializer.data})

    def post(self, request):
        if request.user.is_authenticated:
            album = request.data.get('album')
            album = album[0]
            album["author"] = request.user.id
            serializer = AlbumSerializer(data=album)
            if serializer.is_valid(raise_exception=True):
                album_inst = serializer.save()
            return Response({"success": f"Album '{album_inst.title}' created successfully"})
        return Response({
                'status': 'failed'
            }, status=401)



class PhotoModelView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (MultipartJsonParser, JSONParser)

    def get(self, request):
        photos = Photo.objects.filter(author=request.user.id)
        serializer = PhotoSerializer(photos, context={"request": request}, many=True)
        return Response({'photos': serializer.data})


    def post(self, request, format=None, *args, **kwargs):
        if request.user.is_authenticated:
            photo = request.data.dict().get('photos')
            # print(type(photo), photo, request.user.id)
            photo["author"] = request.user.id
            photo["image"] = request.data.get('media')
            # print(type(photo), photo, request.user.id)
            # file = request.data.get("media")
            # print(file)
            serializer = PhotoSerializer(data=photo)
            if serializer.is_valid(raise_exception=True):
                photo_inst = serializer.save()
            return Response({"success": f"Photo '{photo_inst.title}' created successfully"})
        return Response({
            'status': 'failed'
        }, status=401)


class AlbumTagsView(APIView):
    def get(self, request):
        album_tags = AlbumTags.objects.all()
        serializer = AlbumTagsSerializer(album_tags, many=True)
        return Response({'albums_tags': serializer.data})

    def post(self, request):
        album_tag = request.data.get('album_tag')
        # print(album_tag)
        serializer = AlbumTagsSerializer(data=album_tag)
        if serializer.is_valid(raise_exception=True):
            album_tag_inst = serializer.save()
        return Response({"success": f"Album tag'{album_tag_inst.title}' created successfully"})


class PhotoTagslView(APIView):
    def get(self, request):
        photo_tags = PhotoTags.objects.all()
        serializer = PhotoTagsSerializer(photo_tags, many=True)
        return Response({'photo_tags': serializer.data})

    def post(self, request):
        photo_tag = request.data.get('photo_tag')
        serializer = PhotoTagsSerializer(data=photo_tag)
        if serializer.is_valid(raise_exception=True):
            photo_tag_inst = serializer.save()
        return Response({"success": f"Photo tag'{photo_tag_inst.title}' created successfully"})