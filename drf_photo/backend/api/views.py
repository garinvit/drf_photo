from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import permissions
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, PhotoSerializer, AlbumSerializer, AlbumTagsSerializer, PhotoTagsSerializer
from photo.models import AlbumTags, Album, PhotoTags, Photo


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
    # authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        album = Album.objects.all()
        serializer = AlbumSerializer(album, many=True)
        return Response({'albums': serializer.data})

    def post(self, request):
        if request.user.is_authenticated:
            album = request.data.get('album')
            print(type(request.user.id))
            print(request.POST)
            print(album)
            album["author"] = request.user.id
            serializer = AlbumSerializer(data=album)
            if serializer.is_valid(raise_exception=True):
                album_inst = serializer.save()
            return Response({"success": f"Album '{album_inst.title}' created successfully"})
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