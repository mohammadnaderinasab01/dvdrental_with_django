from rest_framework.test import APITestCase
from django.urls import reverse
from .models import Film
from django.utils import timezone
from utils.test_utils import TestUtils


class FilmListViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('films')

    def test_get_film_list_successful(self):
        language = TestUtils.create_language('English')
        film = TestUtils.create_film(language=language)
        response = self.client.get(self.url)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['film_id'], film.film_id)
        self.assertEqual(response.data['results'][0]['language']['language_id'], language.language_id)
        self.assertEqual(response.data['results'][0]['language']['name'], language.name)
        self.assertEqual(response.data['results'][0]['language']['last_update'].split(".")[0],
                         language.last_update.strftime("%Y-%m-%dT%H:%M:%S"))
        self.assertEqual(response.data['results'][0]['title'], film.title)
        self.assertEqual(response.data['results'][0]['description'], film.description)
        self.assertEqual(response.data['results'][0]['release_year'], film.release_year)
        self.assertEqual(response.data['results'][0]['rental_duration'], film.rental_duration)
        self.assertEqual(response.data['results'][0]['rental_rate'], str(film.rental_rate))
        self.assertEqual(response.data['results'][0]['length'], film.length)
        self.assertEqual(response.data['results'][0]['replacement_cost'], str(film.replacement_cost))
        self.assertEqual(response.data['results'][0]['rating'], film.rating)
        self.assertEqual(response.data['results'][0]['last_update'].split(".")
                         [0], film.last_update.strftime("%Y-%m-%dT%H:%M:%S"))
        self.assertEqual(response.data['results'][0]['special_features'], film.special_features)
        self.assertEqual(response.data['results'][0]['fulltext'], film.fulltext)
