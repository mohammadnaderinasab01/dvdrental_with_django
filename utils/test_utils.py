from films.models import Film, Language
from django.utils import timezone


class TestUtils:
    @staticmethod
    def create_language(name="test_lang"):
        return Language.objects.create(
            name=name,
            last_update=timezone.now()
        )

    @staticmethod
    def create_film(
        language,
        title='test_title',
        last_update=timezone.now(),
        rental_duration=5,
        rental_rate=4.99,
        replacement_cost=19.99,
        release_year=2002,
        length=100,
        rating='R',
        special_features='{test}',
        fulltext='test for text assignment'
    ):
        return Film.objects.create(
            title=title,
            last_update=last_update,
            rental_duration=rental_duration,
            rental_rate=rental_rate,
            replacement_cost=replacement_cost,
            language=language,
            release_year=release_year,
            length=length,
            rating=rating,
            special_features=special_features,
            fulltext=fulltext
        )
