import os
from PIL import Image
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile
from django.db import IntegrityError
from django.test import TestCase    # noqa
from .models import Tags, Photo, Album
# Create your tests here.
UserModel = get_user_model()


class PhotoTest(TestCase):
    fixtures = ['../fixtures/db.json', ]

    def setUp(self):
        self.username = 'username'
        self.password = '12345'

    def test_user(self):
        user = UserModel.objects.create_user(username=self.username, password=self.password)
        user.save()
        # print("user", user.id, user.username)
        instance = UserModel.objects.last()
        self.assertEqual(user, instance)
        with self.assertRaises(IntegrityError):
            user = UserModel.objects.create(username=self.username, password=self.password)

    def test_album(self):
        data = {
            'title': 'TestAlbum',
            'description': 'Test album model',
            'author_id': 1,
        }
        album = Album.objects.create(**data)
        album.save()
        instance = Album.objects.get(title=data.get("title"))
        self.assertEqual(album, instance)
        self.assertEqual(album.get_author(), data.get("author_id"))
        album = Album.objects.get(pk=1)
        self.assertEqual(album.get_photo_count(), Photo.objects.filter(album=album).count())
        self.assertEqual(album.get_photo_count(), 5)
        self.assertEqual(list(album.get_photo_from_album()), list(Photo.objects.filter(album=album)))
        self.assertEqual(len(album.get_photo_from_album()), album.get_photo_count())

    def test_photo(self):
        fp = '../fixtures/car1.jpg'
        img = ImageFile(open(fp, "rb"))
        data = {
            'title': 'TestPhoto',
            'description': 'Test photo model',
            'image': img,
            'image_small': img,
            'album_id': 1
        }
        photo = Photo.objects.create(**data)
        photo.save()
        instance = Photo.objects.get(title='TestPhoto')
        self.assertEqual(photo, instance)
        self.assertEqual(photo.get_author(), instance.album.author.id)
        saved_photo_name = os.path.basename(photo.image_small.name)
        self.assertEqual(saved_photo_name[:6], "small_")
        small_img = Image.open(photo.image_small.path)
        self.assertIn(150, small_img.size)
        # Validation errors
        fp = '../fixtures/large_photo.jpg'
        img = ImageFile(open(fp, "rb"))
        data = {
            'title': 'LargePhotoModel',
            'image': img,
            'image_small': img,
            'album_id': 1
        }
        with self.assertRaises(ValidationError):
            photo = Photo.objects.create(**data)
            photo.save()
        fp = '../fixtures/nyan.gif'
        img = ImageFile(open(fp, "rb"))
        # print(img, dir(img))
        data = {
            'title': 'WrongFormat',
            'image': img,
            'image_small': img,
            'album_id': 1
        }
        with self.assertRaises(ValidationError):
            photo = Photo.objects.create(**data)
            if photo.is_valid():
                photo.save()

    def test_tag(self):
        data = {
            'title': 'test_tag',
        }
        tag = Tags.objects.create(**data)
        tag.save()
        instance = Tags.objects.get(title='test_tag')
        self.assertEqual(tag, instance)
        self.assertEqual(data.get("title"), instance.title)
