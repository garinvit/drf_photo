from rest_framework.test import APIClient
from photo.models import Album, Photo, Tags
from django.contrib.auth import get_user_model
from django.test import TestCase
# Create your tests here.
from django.urls import reverse

UserModel = get_user_model()


class ApiTest(TestCase):
    fixtures = ['../fixtures/db.json', ]

    def setUp(self):
        self.token = "Bearer 677276c4d39c9f3c4d1d776cd292706a2540163b"
        self.username = "admin"
        self.api_client = APIClient()
        self.api_client.credentials(HTTP_AUTHORIZATION=self.token)

    def test_album_get(self):
        response = self.client.get(reverse('api_v3:album-list'), HTTP_ACCEPT='application/json', HTTP_AUTHORIZATION=self.token)
        albums = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(albums), 4)
        self.assertEqual(len(albums), len(Album.objects.filter(author__username=self.username)))
        for i in albums:
            self.assertEqual(i.get("author"), 1)
        response = self.client.get(reverse('api_v3:album-detail', args=[1]), HTTP_ACCEPT='application/json', HTTP_AUTHORIZATION=self.token)
        album = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(album.get("id"), 1)
        response = self.client.get(reverse('api_v3:album-list') + "?search=Толстые", HTTP_ACCEPT='application/json', HTTP_AUTHORIZATION=self.token)
        albums_search_title = response.json()
        self.assertEqual(1, len(albums_search_title))
        response = self.client.get(reverse('api_v3:album-list') + "?search=Отдых", HTTP_ACCEPT='application/json', HTTP_AUTHORIZATION=self.token)
        albums_search_tags = response.json()
        self.assertEqual(3, len(albums_search_tags))
        response = self.client.get(reverse('api_v3:album-detail', args=[4]), HTTP_ACCEPT='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 404)

    def test_album_post(self):
        data = {
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
        response = self.api_client.post(reverse('api_v3:album-list'), data=data, format='json')
        alb = Album.objects.get(pk=int(response.json()["id"]))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(alb.title, data["title"])
        self.assertNotEqual(alb.author, data["author"])

    def test_album_put(self):
        source = self.api_client.get(reverse('api_v3:album-detail', args=[1]), format='json')
        source = source.json()
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
        response = self.api_client.put(reverse('api_v3:album-detail', args=[1]), data=data, format='json')
        alb = Album.objects.get(pk=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(alb.title, data["title"])
        self.assertNotEqual(alb.title, source["title"])
        self.assertNotEqual(alb.author, data["author"])
        response = self.api_client.put(reverse('api_v3:album-detail', args=[4]), format='json')
        self.assertEqual(response.status_code, 404)

    def test_album_delete(self):
        response = self.api_client.delete(reverse('api_v3:album-detail', args=[1]), format='json')
        self.assertEqual(response.status_code, 204)
        deleted = self.api_client.get(reverse('api_v3:album-detail', args=[1]), format='json')
        self.assertEqual(deleted.status_code, 404)
        response = self.api_client.delete(reverse('api_v3:album-detail', args=[4]), format='json')
        self.assertEqual(response.status_code, 404)

    def test_photo_get(self):
        response = self.api_client.get(reverse('api_v3:photo-list'), format='json')
        photos = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(photos), len(Photo.objects.filter(album__author__username=self.username)))
        albums_ids_author = Album.objects.filter(author__username=self.username).values_list('id', flat=True)
        for i in photos:
            self.assertIn(i.get("album"), albums_ids_author)
        response = self.api_client.get(reverse('api_v3:photo-detail', args=[5]), format='json')
        photo = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(photo.get("id"), 5)
        response = self.api_client.get(reverse('api_v3:photo-list') + "?search=Машины", format='json')
        photo_search_tags = response.json()
        self.assertGreaterEqual(len(photos), len(photo_search_tags))
        response = self.client.get(reverse('api_v3:photo-detail', args=[1]), HTTP_ACCEPT='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 404)

    def test_photo_post(self):
        len_photos = len(Photo.objects.all())
        # фото c ссылкой на альбом
        with open('../fixtures/car1.jpg', 'rb') as fp:
            payload = {'data': '{"photos": [{"title": "CarApiTest", "description": "Test post photo api", "album": 2}]}',
                       'media': fp}
            response = self.api_client.post(reverse('api_v3:photo-list'), data=payload, format='multipart')

        photo = Photo.objects.get(title="CarApiTest")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len_photos + 1, len(Photo.objects.all()))
        self.assertEqual(photo.title, "CarApiTest")
        self.assertEqual(photo.album.author.username, self.username)
        payload = {'data': """{"photos": [{"title": "car4", "description": "Несколько фото из апи4", "tags":[1,2], "album": 2},
        {"title": "car5", "description": "Несколько фото из апи5", "tags":[3,4], "album": 2},
        {"title": "car6", "description": "Несколько фото из апи6", "tags":[5,6], "album": 2}]}""",
                   'media': [open('../fixtures/car1.jpg', 'rb'), open('../fixtures/car2.jpg', 'rb'), open('../fixtures/car3.jpeg', 'rb')]
                   }
        response = self.api_client.post(reverse('api_v3:photo-list'), data=payload, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len_photos + 4, len(Photo.objects.all()))
        with open('../fixtures/large_photo.jpg', 'rb') as fp:
            payload = {'data': '{"photos": [{"title": "large_photo", "description": "Test post large photo api", "album": 2}]}', 'media': fp}
            response = self.api_client.post(reverse('api_v3:photo-list'), data=payload, format='multipart')
            self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get("image"), ['Max file size is 5.0MB'])
        with open('../fixtures/nyan.gif', 'rb') as fp:
            payload = {'data': '{"photos": [{"title": "gif", "description": "Test post gif api", "album": 2}]}', 'media': fp}
            response = self.api_client.post(reverse('api_v3:photo-list'), data=payload, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get("image"), ['Не верный формат. Возможны только png, jpg, jpeg.'])

    def test_photo_put(self):
        source = self.api_client.get(reverse('api_v3:photo-detail', args=[5]), format='json')
        source = source.json()
        data = {
            "title": "PUT api test",
            "description": "put test api",
            "album": 2,
            "tags": [1, 2, 3]
        }
        response = self.api_client.put(reverse('api_v3:photo-detail', args=[5]), data=data, format='json')
        photo = Photo.objects.get(pk=5)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(photo.title, data["title"])
        self.assertNotEqual(photo.tags, source["tags"])
        self.assertEqual(photo.album.author.username, self.username)
        response = self.api_client.put(reverse('api_v3:photo-detail', args=[1]), data=data, format='json')
        self.assertEqual(response.status_code, 404)

    def test_photo_delete(self):
        response = self.api_client.delete(reverse('api_v3:photo-detail', args=[5]), format='json')
        self.assertEqual(response.status_code, 204)
        deleted = self.api_client.get(reverse('api_v3:photo-detail', args=[5]), format='json')
        self.assertEqual(deleted.status_code, 404)
        response = self.api_client.delete(reverse('api_v3:photo-detail', args=[1]), format='json')
        self.assertEqual(response.status_code, 404)

    def test_tag_get(self):
        response = self.api_client.get(reverse('api_v3:tags-list'), format='json')
        self.assertEqual(response.status_code, 200)

    def test_tag_post(self):
        response = self.api_client.post(reverse('api_v3:tags-list'), data={"title": "new_tag"}, format='json')
        self.assertEqual(response.status_code, 201)
        tag = response.json()
        self.assertEqual(Tags.objects.get(pk=tag.get("id")).title, "new_tag")
