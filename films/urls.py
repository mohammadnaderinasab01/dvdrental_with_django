from . import views
from django.urls import path


urlpatterns = [
    path('films/', views.FilmListView.as_view(), name="films"),
    path('films/<int:pk>/availability/', views.FilmAvailabilityView.as_view(), name="film_availability"),
    path('actors/', views.ActorListView.as_view(), name="actors"),
    path('film-actors/<int:pk>/', views.FilmActorsView.as_view(), name="film_actors"),
    path('categories/', views.CategoryListView.as_view(), name="categories"),
    path('inventories/', views.InventoryListView.as_view(), name="inventories"),
    path('film-details/<int:pk>/', views.FilmDetailsView.as_view(), name="film_details"),
    path('top-rented-films/', views.TopRentedFilmsView.as_view(), name="top_rented_films"),
    path('most-popular-actors/', views.MostPopularActorsView.as_view(), name="most_popular_actors"),
    path('most-in-used-languages/', views.MostInUsedLanguagesView.as_view(), name='most_in_used_languages'),
    path('create-film/', views.FilmCreateView.as_view(), name='create_film'),
    path('delete-film/<int:pk>/', views.FilmDeleteView.as_view(), name='delete_film'),
    path('most-paid-for-films/', views.MostPaidForFilmsView.as_view(), name='most_paid_for_films'),
    path('actor-films/<int:actor_id>/', views.ActorFilmsView.as_view(), name='actor_films'),
]
