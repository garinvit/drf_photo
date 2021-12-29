from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed, ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, PhotoSerializer, AlbumSerializer, TagsSerializer
from photo.models import Tags, Album, Photo
from app.utils import MultipartJsonParser, MyMethodsMixin


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
        return Response({'status': 'failed'}, status=401)


class AlbumModelView(APIView, MyMethodsMixin):
    permission_classes = (IsAuthenticated,)

    @extend_schema(request=AlbumSerializer, responses={200: AlbumSerializer})
    def get(self, request, pk_album=None, format=None, *args, **kwargs):
        context = {
            "photo_set": request.query_params.get("photos", ""),
            "request": request,
            "display_tags": request.query_params.get("display_tags", ""),
        }
        if pk_album:
            album = self.get_object_from_model(Album, pk_album, request)
            serializer = AlbumSerializer(album, context=context)
            return Response({'album': serializer.data}, status=200)
        else:
            albums = Album.objects.filter(author=request.user.id)
            albums = self.filter_queryset(albums, request)
            serializer = AlbumSerializer(albums, many=True, context=context)
            return Response({'albums': serializer.data}, status=200)

    def post(self, request):
        album = request.data.get('album')
        if album:
            album["author"] = request.user.id
            serializer = AlbumSerializer(data=album)
            if serializer.is_valid(raise_exception=True):
                album_inst = serializer.save()
            return Response({"success": f"Album '{album_inst.title}' created successfully", "id": album_inst.id}, status=201)
        else:
            return Response({'status': 'failed'}, status=400)

    def put(self, request, pk_album=None, format=None):
        if pk_album:
            album = self.get_object_from_model(Album, pk_album, request)
            serializer = AlbumSerializer(album, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"success": "Album update", "update_album": serializer.data}, status=200)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        raise MethodNotAllowed("put")

    def delete(self, request, pk_album=None, format=None):
        if pk_album:
            album = self.get_object_from_model(Album, pk_album, request)
            album.delete()
            return Response({"message": "You delete album"}, status=status.HTTP_204_NO_CONTENT)
        raise MethodNotAllowed("delete")


class PhotoModelView(APIView, MyMethodsMixin):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultipartJsonParser, JSONParser)

    def get(self, request, pk_album=None, pk_photo=None, format=None):
        if pk_photo:
            photo = self.get_object_from_model(Photo, pk_photo, request)
            serializer = PhotoSerializer(photo, context={"request": request})
            return Response({'photo': serializer.data})
        else:
            photos = Photo.objects.filter(album__author__id=request.user.id)
            if pk_album:
                pk_album = self.get_object_from_model(Album, pk_album, request)
                photos = photos.filter(album__id=pk_album.id)
            photos = self.filter_queryset(photos, request)
            serializer = PhotoSerializer(photos, context={"request": request}, many=True)
            return Response({'count': len(serializer.data), 'photos': serializer.data})

    def post(self, request, pk_album=None, format=None, *args, **kwargs):
        print(request.data)
        if pk_album:
            pk_album = self.get_object_from_model(Album, pk_album, request).id
        if request.data:
            photo = request.data.dict().get('photos')
        else:
            return Response({'status': 'failed'}, status=400)
        if isinstance(photo, list):
            files = request.data.getlist("media")
            if len(files) == len(photo):
                files = files[::-1]
                saved_photo = []
                for index, dct in enumerate(photo):
                    photo_dct = {"image": files[index], "image_small": files[index]}
                    photo_dct.update(dct)
                    if not pk_album:
                        album_id = self.get_object_from_model(Album, dct.get("album", None), request).id
                    else:
                        album_id = pk_album
                    photo_dct["album"] = album_id
                    serializer = PhotoSerializer(data=photo_dct)
                    if serializer.is_valid(raise_exception=True):
                        instance = serializer.save()
                        saved_photo.append({"id": instance.id, "title": instance.title})
                return Response({"success created": saved_photo}, status=201)
            else:
                raise ValidationError("Не совпадает количество файлов и записей")
        else:
            photo["image"] = request.data.get('media')
            photo["image_small"] = request.data.get('media')
            if not pk_album:
                pk_album = self.get_object_from_model(Album, photo.get("album", None), request).id
            photo["album"] = pk_album
            serializer = PhotoSerializer(data=photo)
            if serializer.is_valid(raise_exception=True):
                photo_inst = serializer.save()
                return Response({"success": f"Photo '{photo_inst.title}' created successfully", "id": photo_inst.id}, status=201)

    def put(self, request, pk_photo=None, format=None):
        if pk_photo:
            photo = self.get_object_from_model(Photo, pk_photo, request)
            data = request.data.copy()
            album = self.get_object_from_model(Album, data.get("album"), request)  # noqa Проверяем что измененный альбом принадлежит тому же автору
            serializer = PhotoSerializer(photo, data=data, context={"request": request}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"success": "Photo update", "update_photo": serializer.data}, status=200)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        raise MethodNotAllowed("put")

    def delete(self, request, pk_photo=None, format=None):
        if pk_photo:
            photo = self.get_object_from_model(Photo, pk_photo, request)
            photo.delete()
            return Response({"message": "You delete photo"}, status=status.HTTP_204_NO_CONTENT)
        else:
            photos = request.data.get('photo_ids', "")
            if isinstance(photos, list):
                delete_list = []
                for photo in photos:
                    photo_ins = self.get_object_from_model(Photo, photo, request)
                    photo_ins.delete()
                    delete_list.append(photo)
                return Response({"success deleted": delete_list}, status=204)
            else:
                raise ValidationError("Отправьте данные ввиде списка {'photo_ids':[1,2,3]}")
        # raise MethodNotAllowed("delete")


class TagsView(APIView):

    def get(self, request):
        tags = Tags.objects.all()
        serializer = TagsSerializer(tags, many=True)
        return Response({'tags': serializer.data})

    def post(self, request):
        tag = request.data.get('tag')
        serializer = TagsSerializer(data=tag)
        if serializer.is_valid(raise_exception=True):
            tag_inst = serializer.save()
        return Response({"success": f"Tag '{tag_inst.title}' created successfully", "id": tag_inst.id})
