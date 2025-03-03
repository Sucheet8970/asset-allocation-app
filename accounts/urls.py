from django.urls import path
from .views import (
    login_view, dashboard_view, logout_view, inventory_view, new_allocation_view, confirm_receipt,
    faulty_asset_replacement_view, repair_asset_view, update_license_status, asset_deallocation, export_inventory_to_excel, send_allocation_email, export_allocations_to_excel,
    generate_pdf
)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path("inventory/", inventory_view, name="inventory"),
    path("inventory/download/", export_inventory_to_excel, name="export_inventory"),
    path("new_allocation/", new_allocation_view, name="new_allocation"),
    path("faulty_asset_replacement/", faulty_asset_replacement_view, name="faulty_asset_replacement"),
    path("repair_asset/<int:asset_id>/", repair_asset_view, name="repair_asset"),
    path("update-license/<int:laptop_id>/", update_license_status, name="update_license_status"),
    path('deallocation/', asset_deallocation, name='asset_deallocation'),  # Fixed URL to match error
    path('confirmation/<int:allocation_id>/', send_allocation_email, name='confirm_allocation'),
    path("confirm-receipt/<int:id>/", confirm_receipt, name="confirm_receipt"),
    path("new_allocation/download/", export_allocations_to_excel, name="export_allocations"),
    path('generate-pdf/<int:allocation_id>/', generate_pdf, name='generate_pdf'),
]
