from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('customer-payments', views.CustomerPaymentViewSet)


urlpatterns = [
    path('customer-address/', views.CustomerAddressView.as_view()),
    path('customer-rentals/', views.CustomerRentalView.as_view()),
    path('film-recommendations-for-customer/', views.FilmRecommendationsForCustomer.as_view()),
    path('total-payment-amount/', views.CustomerTotalPaymentAmountView.as_view()),
    path('', include(router.urls)),
    path('customer-wishlist/', views.WishListViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='customer_wishlist'),
    path('customer-wishlist/<int:film_id>/', views.WishListViewSet.as_view({
        'delete': 'destroy'
    }), name='delete_customer_wishlist'),
]
