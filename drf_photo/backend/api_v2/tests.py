from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from photo.models import Album, Photo, Tags
from django.contrib.auth import get_user_model
from django.test import TestCase
# Create your tests here.
from django.urls import reverse

UserModel = get_user_model()


class UserTest(TestCase):
    def setUp(self):
        self.username = 'username'
        self.password = '12345'
        self.user = UserModel.objects.create_user(username=self.username, password=self.password)
        self.user.save()

    def test_create_user(self):
        response = self.client.post(
            reverse('api_v2:create-user'),
            {
                'username': "newuser",
                'password': self.password,
            },
            HTTP_ACCEPT='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json().get('username'), "newuser")

    def test_login(self):
        response = self.client.post(
            '/api/v2/auth/login/',
            {
                'username': self.username,
                'password': self.password,
            },
            HTTP_ACCEPT='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json())
        access_token = response.json()['access_token']
        self.token = f'Bearer {access_token}'
        response = self.client.get(reverse('api_v2:current-user'), HTTP_ACCEPT='application/json', HTTP_AUTHORIZATION=f'Bearer {access_token}')
        self.assertEqual(response.json().get('username'), self.username)


class ApiTest(TestCase):
    fixtures = ['../fixtures/db.json', ]

    def setUp(self):
        self.token = "Bearer 677276c4d39c9f3c4d1d776cd292706a2540163b"
        self.username = "admin"
        self.api_client = APIClient()
        self.api_client.credentials(HTTP_AUTHORIZATION=self.token)

    def test_album_get(self):
        response = self.client.get(reverse('api_v2:current-user'), HTTP_ACCEPT='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.json().get('username'), self.username)
        response = self.client.get(reverse('api_v2:album'), HTTP_ACCEPT='application/json', HTTP_AUTHORIZATION=self.token)
        albums = response.json().get("albums")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(albums), 4)
        self.assertEqual(len(albums), len(Album.objects.filter(author__username=self.username)))
        for i in albums:
            self.assertEqual(i.get("author"), 1)
        response = self.client.get(reverse('api_v2:album-pk', args=[1]), HTTP_ACCEPT='application/json', HTTP_AUTHORIZATION=self.token)
        album = response.json().get("album")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(album.get("id"), 1)
        response = self.client.get(reverse('api_v2:album-pk', args=[1]) + "?photos=false&display_tags=false&ordering=id",
                                   HTTP_ACCEPT='application/json', HTTP_AUTHORIZATION=self.token)
        album_excl = response.json().get("album")
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(album.get("tags"), album_excl.get("tags"))
        self.assertNotEqual(album.get("photos"), album_excl.get("photos"))
        response = self.client.get(reverse('api_v2:album') + "?tags=3,4", HTTP_ACCEPT='application/json', HTTP_AUTHORIZATION=self.token)
        albums_search_tags = response.json().get("albums")
        self.assertGreater(len(albums), len(albums_search_tags))
        response = self.client.get(reverse('api_v2:album-pk', args=[4]), HTTP_ACCEPT='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 403)

    def test_album_post(self):
        data = {
            "album":
                {
                    "title": "Новый альбом",
                    "description": "Созданный из апи",
                    "author": 2,
                    "tags": [
                        1,
                        2,
                        3,
                        4
                    ]
                }
        }
        response = self.api_client.post(reverse('api_v2:album'), data=data, format='json')
        alb = Album.objects.get(pk=int(response.json()["id"]))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(alb.title, data["album"]["title"])
        self.assertNotEqual(alb.author, data["album"]["author"])

    def test_album_put(self):
        source = self.api_client.get(reverse('api_v2:album-pk', args=[1]), format='json')
        source = source.json()["album"]
        data = {
            "title": "Изменил название",
            "description": "Созданный из апи",
            "author": 2,
            "tags": [
                1,
                3,
                4
            ]
        }
        response = self.api_client.put(reverse('api_v2:album-pk', args=[1]), data=data, format='json')
        alb = Album.objects.get(pk=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(alb.title, data["title"])
        self.assertNotEqual(alb.title, source["title"])
        self.assertNotEqual(alb.author, data["author"])
        response = self.api_client.put(reverse('api_v2:album'), data=data, format='json')
        self.assertEqual(response.status_code, 405)
        response = self.api_client.put(reverse('api_v2:album-pk', args=[4]), format='json')
        self.assertEqual(response.status_code, 403)

    def test_album_delete(self):
        response = self.api_client.delete(reverse('api_v2:album-pk', args=[1]), format='json')
        self.assertEqual(response.status_code, 204)
        deleted = self.api_client.get(reverse('api_v2:album-pk', args=[1]), format='json')
        self.assertEqual(deleted.status_code, 404)
        response = self.api_client.delete(reverse('api_v2:album-pk', args=[4]), format='json')
        self.assertEqual(response.status_code, 403)

    def test_photo_get(self):
        response = self.api_client.get(reverse('api_v2:photo'), format='json')
        photos = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(photos.get("photos")), len(Photo.objects.filter(album__author__username=self.username)))
        self.assertEqual(len(photos.get("photos")), response.json()["count"])
        albums_ids_author = [alb.id for alb in Album.objects.all()]
        for i in photos.get("photos"):
            self.assertIn(i.get("album"), albums_ids_author)
        response = self.api_client.get(reverse('api_v2:photo-pk', args=[5]), format='json')
        photo = response.json().get("photo")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(photo.get("id"), 5)
        response = self.api_client.get(reverse('api_v2:photo') + "?tags=3,4", format='json')
        photo_search_tags = response.json()
        self.assertGreaterEqual(photos.get("count"), photo_search_tags.get("count"))
        response = self.api_client.get(reverse('api_v2:photo-album-pk', args=[1]), format='json')
        photos = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(photos.get("count"), len(Photo.objects.filter(album__id=1)))
        for i in photos.get("photos"):
            self.assertEqual(i.get("album"), 1)
        response = self.client.get(reverse('api_v2:photo-pk', args=[1]), HTTP_ACCEPT='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 403)

    def test_photo_post(self):
        # print(Photo.objects.all())
        # фото c ссылкой на альбом
        with open('../fixtures/Cat1.jpeg', 'rb') as fp:
            payload = {'data': '{"photos": {"title": "CatApiTest", "description": "Test post photo api"}}', 'media': fp}
            response = self.api_client.post(reverse('api_v2:photo-album-pk', args=[1]), data=payload, format='multipart')
        id = response.json().get("id")
        photo = Photo.objects.get(pk=id)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(photo.title, "CatApiTest")
        self.assertEqual(photo.album.author.username, self.username)
        # фото с указанием альбома
        with open('../fixtures/car1.jpg', 'rb') as fp:
            payload = {'data': '{"photos": {"title": "CarApiTest", "description": "Test post photo api", "album": 2}}',
                       'media': fp}
            response = self.api_client.post(reverse('api_v2:photo'), data=payload, format='multipart')
        id = response.json().get("id")
        photo = Photo.objects.get(pk=id)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(photo.title, "CarApiTest")
        self.assertEqual(photo.album.author.username, self.username)
        # много фото альбом из ссылки
        payload = {'data': """{"photos": [{"title": "car1", "description": "Несколько фото из апи1", "tags":[1,2]},
                                        {"title": "car2", "description": "Несколько фото из апи2", "tags":[3,4]}, 
                                        {"title": "car3", "description": "Несколько фото из апи3", "tags":[5,6]}]}""",
                    'media': [open('../fixtures/car1.jpg', 'rb'), open('../fixtures/car2.jpg', 'rb'), open('../fixtures/car3.jpeg', 'rb')]
                   }
        response = self.api_client.post(reverse('api_v2:photo-album-pk', args=[1]), data=payload, format='multipart')
        self.assertEqual(response.status_code, 201)
        new_photos = response.json().get('success created')
        for photo in new_photos:
            get_photo = Photo.objects.get(pk=photo.get("id"))
            self.assertEqual(get_photo.title, photo.get("title"))
        # много фото с указанием альбома
        payload = {'data': """{"photos": [{"title": "car4", "description": "Несколько фото из апи4", "tags":[1,2], "album": 2},
                                        {"title": "car5", "description": "Несколько фото из апи5", "tags":[3,4], "album": 2}, 
                                        {"title": "car6", "description": "Несколько фото из апи6", "tags":[5,6], "album": 2}]}""",
                   'media': [open('../fixtures/car1.jpg', 'rb'), open('../fixtures/car2.jpg', 'rb'), open('../fixtures/car3.jpeg', 'rb')]
                   }
        response = self.api_client.post(reverse('api_v2:photo'), data=payload, format='multipart')
        self.assertEqual(response.status_code, 201)
        new_photos = response.json().get('success created')
        for photo in new_photos:
            get_photo = Photo.objects.get(pk=photo.get("id"))
            self.assertEqual(get_photo.title, photo.get("title"))
        # Validation Errors
        with open('../fixtures/large_photo.jpg', 'rb') as fp:
            payload = {'data': '{"photos": {"title": "large_photo", "description": "Test post large photo api"}}', 'media': fp}
            response = self.api_client.post(reverse('api_v2:photo-album-pk', args=[1]), data=payload, format='multipart')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json().get("image"), ['Max file size is 5.0MB'])
        with open('../fixtures/nyan.gif', 'rb') as fp:
            payload = {'data': '{"photos": {"title": "gif", "description": "Test post gif photo api"}}', 'media': fp}
            response = self.api_client.post(reverse('api_v2:photo-album-pk', args=[1]), data=payload, format='multipart')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json().get("image"), ['Не верный формат. Возможны только png, jpg, jpeg.'])

    def test_photo_put(self):
        source = self.api_client.get(reverse('api_v2:photo-pk', args=[5]), format='json')
        source = source.json()["photo"]
        data = {
            "title": "PUT api test",
            "description": "put test api",
            "album": 2,
            "tags": [1, 2, 3]
        }
        response = self.api_client.put(reverse('api_v2:photo-pk', args=[5]), data=data, format='json')
        photo = Photo.objects.get(pk=5)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(photo.title, data["title"])
        self.assertNotEqual(photo.tags, source["tags"])
        self.assertEqual(photo.album.author.username, self.username)
        response = self.api_client.put(reverse('api_v2:photo-pk', args=[1]), data=data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_photo_delete(self):
        response = self.api_client.delete(reverse('api_v2:photo-pk', args=[5]), format='json')
        self.assertEqual(response.status_code, 204)
        response = self.api_client.delete(reverse('api_v2:photo'), data={"photo_ids": [6, 7, 8]}, format='json')
        deleted = response.data.get('success deleted')
        for id in deleted:
            del_photo = self.api_client.get(reverse('api_v2:photo-pk', args=[id]), format='json')
            self.assertEqual(del_photo.status_code, 404)
        self.assertEqual(response.status_code, 204)
        deleted = self.api_client.get(reverse('api_v2:photo-pk', args=[5]), format='json')
        self.assertEqual(deleted.status_code, 404)
        response = self.api_client.delete(reverse('api_v2:photo-pk', args=[1]), format='json')
        self.assertEqual(response.status_code, 403)

    def test_tag_get(self):
        response = self.api_client.get(reverse('api_v2:tags'), format='json')
        self.assertEqual(response.status_code, 200)

    def test_tag_post(self):
        response = self.api_client.post(reverse('api_v2:tags'), data={"tag": {"title": "new_tag"}}, format='json')
        self.assertEqual(response.status_code, 200)
        tag = response.json()
        self.assertEqual(Tags.objects.get(pk=tag.get("id")).title, "new_tag")