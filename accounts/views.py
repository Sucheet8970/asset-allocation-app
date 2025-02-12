from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from .models import Inventory, Laptop, Allocation 
from django.contrib.auth.decorators import user_passes_test


# User Authentication Views
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'accounts/login.html')

@login_required
def dashboard_view(request):
    total_laptops = Inventory.objects.count()
    confirmed_allocations = Allocation.objects.filter(confirmed=True).count()
    pending_confirmations = Allocation.objects.filter(confirmed=False).count()

    # ✅ Fetch allocations with related laptop data
    asset_data = Allocation.objects.select_related("laptop").values(
        "id", 
        "engineer_name", 
        "laptop__asset_host_name",  # ✅ Fetch asset host name from Inventory
        "laptop__license_status",   # ✅ Fetch license status from Inventory
        "confirmed"
    )

    # ✅ Ensure allocation_status is included
    for asset in asset_data:
        laptop = Inventory.objects.filter(asset_host_name=asset["laptop__asset_host_name"]).first()
        asset["allocation_status"] = laptop.allocation_status if laptop else "Available"

    context = {
        "total_laptops": total_laptops,
        "confirmed_allocations": confirmed_allocations,
        "pending_confirmations": pending_confirmations,
        "asset_data": asset_data
    }
    return render(request, "accounts/dashboard.html", context)

def logout_view(request):
    logout(request)
    return redirect('login')

# Inventory Management
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Inventory

@login_required

@login_required

@login_required
def inventory_view(request):
    search_query = request.GET.get("search", "").strip()  # ✅ Get search query

    if search_query:
        laptops = Inventory.objects.filter(asset_host_name__icontains=search_query)  # ✅ Search by Asset Host Name
    else:
        laptops = Inventory.objects.all()

    application_choices = ["Sophos Antivirus", "Patch Manager", "SASE Proxy Agent", "Summit"]

    if request.method == "POST":
        action = request.POST.get("action", "")

        if action == "add":
            asset_host_name = request.POST.get("asset_host_name")

            # ✅ Prevent duplicate asset host names
            if Inventory.objects.filter(asset_host_name=asset_host_name).exists():
                messages.error(request, f"Asset Host Name '{asset_host_name}' already exists!")
                return redirect("inventory")

            installed_apps = request.POST.getlist("installed_apps")

            Inventory.objects.create(
                asset_host_name=asset_host_name,
                installed_apps=", ".join(installed_apps),
                allocation_status="Available",  # ✅ Set default as "Available"
                license_status="Pending",  # ✅ Default license status
            )
            messages.success(request, "New laptop added successfully!")
            return redirect("inventory")

        elif action == "edit":
            laptop_id = request.POST.get("laptop_id")
            laptop = get_object_or_404(Inventory, id=laptop_id)
            new_asset_host_name = request.POST.get("asset_host_name")

            if Inventory.objects.filter(asset_host_name=new_asset_host_name).exclude(id=laptop_id).exists():
                messages.error(request, f"Asset Host Name '{new_asset_host_name}' already exists!")
                return redirect("inventory")

            laptop.asset_host_name = new_asset_host_name
            laptop.installed_apps = ", ".join(request.POST.getlist("installed_apps"))
            laptop.save()

            messages.success(request, "Laptop updated successfully!")
            return redirect("inventory")

        elif action == "delete":
            laptop_id = request.POST.get("laptop_id")
            laptop = get_object_or_404(Inventory, id=laptop_id)
            laptop.delete()

            messages.success(request, "Laptop deleted successfully!")
            return redirect("inventory")

    return render(request, "accounts/inventory.html", {
        "laptops": laptops,
        "application_choices": application_choices,
        "search_query": search_query,
    })

def is_license_engineer(user):
    return user.groups.filter(name="License Engineers").exists()

@login_required
@user_passes_test(is_license_engineer)
def update_license_status(request, laptop_id):
    laptop = get_object_or_404(Inventory, id=laptop_id)

    if request.method == "POST":
        print("📩 Received Form Data:", request.POST)  # Debugging Line

        laptop.sophos_status = request.POST.get("sophos_status", "Pending")
        laptop.patch_manager_status = request.POST.get("patch_manager_status", "Pending")
        laptop.sase_proxy_status = request.POST.get("sase_proxy_status", "Pending")
        laptop.summit_status = request.POST.get("summit_status", "Pending")

        # ✅ Check if all are confirmed, then update main status
        if (laptop.sophos_status == "Confirmed" and 
            laptop.patch_manager_status == "Confirmed" and 
            laptop.sase_proxy_status == "Confirmed" and 
            laptop.summit_status == "Confirmed"):
            laptop.license_status = "Active"
        else:
            laptop.license_status = "Pending"

        laptop.save()

        print("✅ Updated Status:", laptop.sophos_status, laptop.patch_manager_status, laptop.sase_proxy_status, laptop.summit_status, laptop.license_status)  # Debugging Line

    return redirect("inventory")




# Laptop Allocation
@login_required
def new_allocation_view(request):
    available_laptops = Inventory.objects.filter(allocation_status="Available")
    allocated_laptops = Allocation.objects.select_related("laptop").all()  

    if request.method == "POST":
        print("📩 Received Form Data:", request.POST)

        engineer_name = request.POST.get("engineer_name")
        email = request.POST.get("email")
        laptop_id = request.POST.get("laptop")

        if engineer_name and email and laptop_id:
            try:
                laptop = Inventory.objects.get(id=laptop_id)  # ✅ Fetch from Inventory
                print("✅ Laptop Found:", laptop.asset_host_name)

                allocation = Allocation.objects.create(
                    laptop=laptop,
                    engineer_name=engineer_name,
                    email=email
                )

                # Mark laptop as allocated
                laptop.allocation_status = "Allocated"
                laptop.save(update_fields=["allocation_status"])  # ✅ Ensures only status is updated

                print("✅ Allocation Saved:", allocation)

                send_allocation_email(allocation)

                messages.success(request, "Laptop allocated successfully!")
                return redirect("new_allocation")

            except Inventory.DoesNotExist:
                print("❌ Laptop Not Found in Inventory!")
                messages.error(request, "Selected laptop does not exist!")

    return render(request, "accounts/new_allocation.html", {
        "available_laptops": available_laptops,
        "allocated_laptops": allocated_laptops,
    })


def send_allocation_email(allocation):
    confirmation_url = f"http://127.0.0.1:8000/confirm-receipt/{allocation.id}/"
    
    subject = "Laptop Allocation Confirmation"
    message = f"""
Dear {allocation.engineer_name},

You have been allocated a laptop with the following details:

- **Asset Host Name:** {allocation.laptop.asset_host_name}  ✅ FIXED: Access via `laptop`
- **Allocation Date:** {allocation.allocation_date}

Please confirm the receipt of this laptop by clicking the link below:

{confirmation_url}

Regards,  
IT Team
"""

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [allocation.email])

@login_required
def confirm_receipt(request, allocation_id):
    allocation = get_object_or_404(Allocation, id=allocation_id)
    
    if not allocation.confirmed:
        allocation.confirmed = True
        allocation.save()
    
    return HttpResponse("<h2>✅ Thank you! Your receipt has been confirmed.</h2>")

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Inventory, Allocation

# 🔹 Faulty Asset Replacement
@login_required
def faulty_asset_replacement_view(request):
    search_query = request.GET.get("search", "").strip()

    # 🔹 Get **Allocated** assets for dropdown
    allocated_assets = Inventory.objects.filter(allocation_status="Allocated")

    # 🔹 Get **Decommissioned** assets for the table
    decommissioned_assets = Inventory.objects.filter(allocation_status="Decommissioned")

    # 🔹 Apply search filter
    if search_query:
        allocated_assets = allocated_assets.filter(asset_host_name__icontains=search_query)
        decommissioned_assets = decommissioned_assets.filter(asset_host_name__icontains=search_query)

    # 🔹 Get available laptops for replacement
    available_laptops = Inventory.objects.filter(allocation_status="Available")

    if request.method == "POST":
        faulty_asset_id = request.POST.get("faulty_asset_id")
        replacement_asset_id = request.POST.get("replacement_asset_id")

        if faulty_asset_id and replacement_asset_id:
            faulty_asset = get_object_or_404(Inventory, id=faulty_asset_id)
            replacement_asset = get_object_or_404(Inventory, id=replacement_asset_id)

            # ✅ Find engineer assigned to faulty asset
            allocation_entry = Allocation.objects.filter(laptop=faulty_asset).first()

            # ✅ Mark faulty asset as "Decommissioned" and store replaced asset
            faulty_asset.allocation_status = "Decommissioned"
            faulty_asset.replaced_with = replacement_asset  # Store replaced asset
            faulty_asset.save()

            # ✅ Assign the replacement asset to the same engineer
            if allocation_entry:
                allocation_entry.laptop = replacement_asset  # Update allocation
                allocation_entry.save()

            # ✅ Mark the replacement asset as "Allocated"
            replacement_asset.allocation_status = "Allocated"
            replacement_asset.save()

            messages.success(request, "Faulty asset replaced successfully!")
            return redirect("faulty_asset_replacement")

    return render(request, "accounts/faulty_asset_replacement.html", {
        "allocated_assets": allocated_assets,
        "decommissioned_assets": decommissioned_assets,
        "available_laptops": available_laptops,
        "search_query": search_query,
    })

# 🔹 Repair Asset View with Search
@login_required
def repair_asset_view(request, asset_id=None):  # Ensure `asset_id` is an argument
    if asset_id is None:
        messages.error(request, "Invalid asset ID.")
        return redirect("faulty_asset_replacement")

    asset = get_object_or_404(Inventory, id=asset_id, allocation_status="Decommissioned")

    # ✅ Mark the asset as "Available" again
    asset.allocation_status = "Available"
    asset.replaced_with = None  # Remove replaced laptop reference
    asset.last_assigned_engineer = None  # Remove engineer name
    asset.save()

    messages.success(request, f"{asset.asset_host_name} has been repaired and is now available.")
    return redirect("faulty_asset_replacement")

'''---------------------------------------------------------------------------------------------------------------------------------------------------'''
@login_required
def deallocation_view(request):
    """Handles deallocating assets from ex-employees and displays deallocated assets."""

    # 🔹 Get employees who currently have an allocated laptop
    allocated_employees = Allocation.objects.filter(laptop__allocation_status="Allocated")

    # 🔹 Get deallocated laptops (previously allocated but now available)
    deallocated_assets = Inventory.objects.filter(
    allocation_status="Available"
).exclude(id__in=Allocation.objects.values_list("laptop_id", flat=True))


    selected_employee_id = request.GET.get("employee_id")
    selected_employee = None
    allocated_laptop = None

    if selected_employee_id:
        selected_employee = get_object_or_404(Allocation, id=selected_employee_id)
        allocated_laptop = selected_employee.laptop  # Get the allocated laptop

    if request.method == "POST":
        employee_id = request.POST.get("employee_id")
        data_transfer_status = request.POST.get("data_transfer_status")
        
        if employee_id:
            allocation = get_object_or_404(Allocation, id=employee_id)
            laptop = allocation.laptop

            # ✅ Mark laptop as "Available"
            laptop.allocation_status = "Available"
            laptop.data_transfer_status = data_transfer_status  # Save data transfer status
            laptop.save()

            # ✅ Remove allocation entry
            allocation.delete()

            messages.success(request, f"Laptop {laptop.asset_host_name} has been deallocated and is now available.")
            return redirect("deallocation")

    return render(request, "accounts/deallocation.html", {
        "allocated_employees": allocated_employees,
        "selected_employee": selected_employee,
        "allocated_laptop": allocated_laptop,
        "deallocated_assets": deallocated_assets,
    })

def format_laptop_view(request, asset_id):
    asset = get_object_or_404(Inventory, id=asset_id, allocation_status="Deallocated")

    # ✅ Clear installed applications permanently
    asset.installed_applications = ""
    asset.save()

    messages.success(request, f"All installed applications have been removed from {asset.asset_host_name}.")
    return redirect("deallocation")