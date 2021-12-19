from django.contrib.auth import get_user_model
from django.http import Http404
from rest_framework import permissions, status
from rest_framework.decorators import parser_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import MultiPartParser, FileUploadParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, PhotoSerializer, AlbumSerializer, AlbumTagsSerializer, PhotoTagsSerializer
from photo.models import AlbumTags, Album, PhotoTags, Photo
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

    def get_object(self, pk, request):
        try:
            obj = Album.objects.get(pk=pk)
            if obj.author.id != request.user.id:
                # return Response(status=403)
                raise PermissionDenied({"message": "You don't have permission to access"})
            else:
                return obj
        except Album.DoesNotExist:
            raise Http404

    def get(self, request, pk=None, format=None, *args, **kwargs):
        if pk:
            album = self.get_object(pk, request)
            serializer = AlbumSerializer(album, context={"request": request})
            return Response({'album': serializer.data})
        else:
            albums = Album.objects.filter(author=request.user.id)
            params = request.query_params.get("ordering")
            tags = request.query_params.get("tags")
            if tags:
                tags = map(int, request.query_params.get("tags").split(","))
                for tag in tags:
                    albums = albums.filter(tags__id=tag).distinct()
            if params:
                if params == "count":
                    # albums = albums.order_by(Length('photo__set').asc())
                    # albums = albums.order_by('photo__set__count').distinct()
                    # albums = albums.order_by('photo__length').distinct()
                    albums = sorted(albums, key=lambda x: x.get_photo_count())
                elif params == "-count":
                    albums = sorted(albums, key=lambda x: x.get_photo_count())
                    # albums = albums.order_by('-photo__length').distinct()
                else:
                    albums = albums.order_by(params)
            serializer = AlbumSerializer(albums, many=True, context={"request": request})
            return Response({'albums': serializer.data})

    def post(self, request):
        if request.user.is_authenticated:
            album = request.data.get('album')
            album["author"] = request.user.id
            serializer = AlbumSerializer(data=album)
            if serializer.is_valid(raise_exception=True):
                album_inst = serializer.save()
            return Response({"success": f"Album '{album_inst.title}' created successfully", "id": album_inst.id})
        return Response({
                'status': 'failed'
            }, status=401)

    def put(self, request, pk, format=None):
        album = self.get_object(pk, request)
        serializer = AlbumSerializer(album, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Album update", "update_album": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        album = self.get_object(pk, request)
        album.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PhotoModelView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (MultipartJsonParser, JSONParser)

    def get_object(self, pk, request):
        try:
            obj = Photo.objects.get(pk=pk)
            if obj.author.id != request.user.id:
                raise PermissionDenied({"message": "You don't have permission to access"})
            else:
                return obj
        except Photo.DoesNotExist:
            raise Http404

    def get(self, request, pk=None, format=None):
        if pk:
            photo = self.get_object(pk, request)
            serializer = PhotoSerializer(photo, context={"request": request})
            return Response({'photo': serializer.data})
        else:
            photos = Photo.objects.filter(author=request.user.id)
            params = request.query_params.get("ordering")
            tags = request.query_params.get("tags")
            if tags:
                tags = map(int, request.query_params.get("tags").split(","))
                for tag in tags:
                    photos = photos.filter(tags__id=tag).distinct()
            if params:
                photos = photos.order_by(params)
            serializer = PhotoSerializer(photos, context={"request": request}, many=True)
            return Response({'count': len(serializer.data), 'photos': serializer.data})

    def post(self, request, format=None, *args, **kwargs):
        if request.user.is_authenticated:
            photo = request.data.dict().get('photos')
            # print(type(photo), photo, request.user.id)
            photo["author"] = request.user.id
            photo["image"] = request.data.get('media')
            photo["image_small"] = request.data.get('media')
            print(type(photo), photo, request.user.id)
            serializer = PhotoSerializer(data=photo)
            if serializer.is_valid(raise_exception=True):
                photo_inst = serializer.save()
                return Response({"success": f"Photo '{photo_inst.title}' created successfully", "id": photo_inst.id})
        return Response({
            'status': 'failed'
        }, status=401)

    def put(self, request, pk, format=None):
        photo = self.get_object(pk, request)
        data = request.data.copy()
        data["author"] = request.user.id
        serializer = PhotoSerializer(photo, data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Photo update", "update_photo": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        photo = self.get_object(pk, request)
        photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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