from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('customer-payments', views.CustomerPaymentViewSet)
router.register('customer-wishlist', views.WishListViewSet)


urlpatterns = [
    path('customer-address/', views.CustomerAddressView.as_view()),
    path('customer-rentals/', views.CustomerRentalView.as_view()),
    path('film-recommendations-for-customer/', views.FilmRecommendationsForCustomer.as_view()),
    path('total-payment-amount/', views.CustomerTotalPaymentAmountView.as_view()),
    path('', include(router.urls)),
]
