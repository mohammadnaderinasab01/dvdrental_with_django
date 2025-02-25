from . import views
from django.urls import path


urlpatterns = [
    path('films/', views.FilmListView.as_view(), name="films"),
    path('films/<int:pk>/availability/', views.FilmAvailabilityView.as_view(), name="film_availability"),
    path('actors/', views.ActorListView.as_view(), name="actors"),
    path('categories/', views.CategoryListView.as_view(), name="categories"),
    path('inventories/', views.InventoryListView.as_view(), name="inventories"),
    path('film-details/<int:pk>/', views.FilmDetailsView.as_view(), name="film_details"),
    path('top-rented-films/', views.TopRentedFilmsView.as_view(), name="top_rented_films"),
    path('most-popular-actors/', views.MostPopularActorsView.as_view(), name="most_popular_actors"),
    path('most-in-used-languages/', views.MostInUsedLanguagesView.as_view(), name='most_in_used_languages'),
]
