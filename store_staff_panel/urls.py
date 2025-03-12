from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register('payments', views.StaffPaymentView)

urlpatterns = [
    path('return-rental/<int:pk>/', views.ReturnRentalView.as_view(), name="return_rental"),
    path('rent-film/', views.RentFilmView.as_view(), name="rent_film"),
    path('', include(router.urls)),
    path('total-revenue/', views.TotalRevenueView.as_view(), name='total_revenue'),
    path('add-film-inventory/<int:pk>/', views.AddFilmInventoryToStoreView.as_view(), name="add_film"),
    path('remove-inventory/<int:pk>/', views.RemoveInventoryFromStoreView.as_view(), name='remove_inventory'),
    path('remove-all-film-inventories-from-store/<int:pk>/',
         views.RemoveAllFilmInventoriesFromStoreView.as_view(),
         name="remove_all_film_inventories_from_store"),
    path('inventory-statistics/', views.InventoryStatisticsView.as_view(), name='inventory_statistics'),
]
