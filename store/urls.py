from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register('stores', views.StoreViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('top-rented-films-by-store/', views.TopRentedFilmsByStoreView.as_view()),
    path('most-renting-customer/', views.MostRentingCustomerView.as_view()),
]
