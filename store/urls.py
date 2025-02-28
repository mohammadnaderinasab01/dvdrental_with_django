from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register('stores', views.StoreViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('top-rented-films-by-store/', views.TopRentedFilmsByStoreView.as_view()),
    path('most-renting-customer/', views.MostRentingCustomerView.as_view()),
    path('total-payment-amount-for-store/',
         views.TotalPaymentAmountForStoreView.as_view(),
         name='total_payment_amount_for_store'),
    path('non-returned-film-inventories/', views.NonReturnedFilmInventoriesView.as_view(), name='non_returned_films'),
    path('top-store-inventories-total-renting/',
         views.TopStoreInventoriesTotalRentingView.as_view(),
         name='top_store_inventories_total_renting'),
]
