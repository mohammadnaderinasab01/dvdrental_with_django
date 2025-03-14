from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register('customers', views.CustomerViewSet)
router.register('staffs', views.StaffViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('top-renting-customers/', views.TopRentingCustomersView.as_view()),
    path('store-total-revenue/<int:pk>/', views.StoreTotalRevenueView.as_view()),
    path('top-performing-stores/', views.TopPerformingStoresView.as_view()),
    path('countries-having-most-customers/', views.CountriesHavingMostCustomersView.as_view()),
    path('add-actor-to-film-by-film-id/<int:pk>/', views.AddActorToFilmView.as_view()),
    path('remove-actor-from-film-by-film-id/<int:pk>/', views.RemoveActorFromFilmView.as_view()),
    path('customers-wishlist/', views.WishListViewSet.as_view({
        'get': 'list',
    }), name='customer_wishlist'),
    path('customer-wishlist/<int:customer_id>/', views.CustomerWishListView.as_view(), name="customer_wishlist"),
    path('top-score-films-list/', views.TopScoreFilmsListView.as_view(), name='top_score_films_list'),
    path('film-score/<int:pk>/', views.FilmScoreView.as_view(), name='film_score'),
    path('most-rental-duration-average-customers/',
         views.MostRentalDurationAverageCustomersView.as_view(),
         name='most_rental_duration_average_customers'),
    path('most-kept-films/', views.MostKeptFilmsListView.as_view(), name='most_kept_films'),
    path('most-wished-films/', views.MostWishedFilmsListView.as_view(), name='most_wished_films'),
]
