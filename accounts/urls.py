from django.urls import path
from .views import login_view, dashboard_view, logout_view, inventory_view, new_allocation_view, confirm_receipt, faulty_asset_replacement_view, repair_asset_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),  # New dashboard URL
    path('logout/', logout_view, name='logout'),
    path("inventory/", inventory_view, name="inventory"),
    path("new_allocation/", new_allocation_view, name="new_allocation"),
    path("confirm-receipt/<int:allocation_id>/", confirm_receipt, name="confirm-receipt"),
    path("faulty_asset_replacement/", faulty_asset_replacement_view, name="faulty_asset_replacement"),
    path("repair_asset/<int:asset_id>/", repair_asset_view, name="repair_asset"),
]
