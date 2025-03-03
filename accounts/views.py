from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from .models import Inventory, Laptop, Allocation, Deallocation 
from django.contrib.auth.decorators import user_passes_test
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.template.loader import get_template
import pdfkit
from django.template.loader import render_to_string, get_template
import csv
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from weasyprint import HTML
import tempfile
import os



'''--------------------------------------------------------------LOGIN------------------------------------------------------------------------------'''
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
'''--------------------------------------------------------------------DASHBOARD-----------------------------------------------------------------------'''
@login_required
def dashboard_view(request):
    total_laptops = Inventory.objects.count()
    confirmed_allocations = Allocation.objects.filter(confirmed=True).count()
    pending_confirmations = Allocation.objects.filter(confirmed=False).count()

    # ✅ Count the number of laptops where all licenses are confirmed
    confirmed_licenses = Inventory.objects.filter(
        sophos_status="Confirmed",
        patch_manager_status="Confirmed",
        sase_proxy_status="Confirmed",
        summit_status="Confirmed"
    ).count()

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
        "confirmed_licenses": confirmed_licenses,  # ✅ New context variable for confirmed licenses
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

'''--------------------------------------------------------------------INVENTORY---------------------------------------------------------------------------------------------------------------------'''
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
        
        # ✅ Add confirmed licenses for each laptop
    for laptop in laptops:
        confirmed_licenses = []
        if laptop.sophos_status == "Confirmed":
            confirmed_licenses.append("Sophos Antivirus")
        if laptop.patch_manager_status == "Confirmed":
            confirmed_licenses.append("Patch Manager")
        if laptop.sase_proxy_status == "Confirmed":
            confirmed_licenses.append("SASE Proxy Agent")
        if laptop.summit_status == "Confirmed":
            confirmed_licenses.append("Summit")
        laptop.confirmed_licenses = ", ".join(confirmed_licenses) if confirmed_licenses else "None"


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

@login_required
def export_inventory_to_excel(request):
    """Generate an Excel file of the inventory and serve it as a download."""
    laptops = Inventory.objects.all()

    # ✅ Prepare data for the Excel file
    data = []
    for laptop in laptops:
        confirmed_licenses = []
        if laptop.sophos_status == "Confirmed":
            confirmed_licenses.append("Sophos Antivirus")
        if laptop.patch_manager_status == "Confirmed":
            confirmed_licenses.append("Patch Manager")
        if laptop.sase_proxy_status == "Confirmed":
            confirmed_licenses.append("SASE Proxy Agent")
        if laptop.summit_status == "Confirmed":
            confirmed_licenses.append("Summit")

        data.append([
            laptop.asset_host_name,
            laptop.installed_apps,
            laptop.license_status,
            ", ".join(confirmed_licenses) if confirmed_licenses else "None"
        ])

    # ✅ Create a Pandas DataFrame
    df = pd.DataFrame(data, columns=["Asset Host Name", "Installed Applications", "License Status", "Confirmed Licenses"])

    # ✅ Convert DataFrame to Excel format
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="inventory.xlsx"'
    
    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Inventory", index=False)

    return response


'''-----------------------------------------------------------------------------new_allocation-----------------------------------------------------------------------------------------'''
# Laptop Allocation
@login_required
def new_allocation_view(request):
    available_laptops = Inventory.objects.filter(allocation_status__in=["Available", "Deallocated"])
    allocated_laptops = Allocation.objects.select_related("laptop").all()

    if request.method == "POST":
        print("📩 Received Form Data:", request.POST)

        engineer_name = request.POST.get("engineer_name")
        email = request.POST.get("email")
        laptop_id = request.POST.get("laptop")

        # Custodian Details
        emp_id = request.POST.get("emp_id")
        location = request.POST.get("location")
        building = request.POST.get("building")
        seat_no = request.POST.get("seat_no")
        contact_no = request.POST.get("contact_no")
        request_no = request.POST.get("request_no")
        department = request.POST.get("department")
        manager = request.POST.get("manager")

        # Allocation Category
        project_specific = request.POST.get("project_specific")

        # Asset Category
        laptop_category = request.POST.get("laptop_category")
        other_assets = request.POST.get("other_assets", "")  # Optional

        # Asset Allocation Type
        short_term = request.POST.get("short_term")

        # Hardware Details
        manufacturer = request.POST.get("manufacturer")
        processor = request.POST.get("processor")
        adapter = request.POST.get("adapter")
        asset_tag_number = request.POST.get("asset_tag_number")
        ram_size = request.POST.get("ram_size")
        mouse = request.POST.get("mouse")
        serial_number = request.POST.get("serial_number")
        model = request.POST.get("model")
        hard_disk = request.POST.get("hard_disk")
        bag = request.POST.get("bag")
        battery_sl = request.POST.get("battery_sl")
        other_description = request.POST.get("other_description", "")  # Optional

        if engineer_name and email and laptop_id:
            try:
                laptop = Inventory.objects.get(id=laptop_id)  # ✅ Fetch from Inventory
                print("✅ Laptop Found:", laptop.asset_host_name)

                allocation = Allocation.objects.create(
                    laptop=laptop,
                    engineer_name=engineer_name,
                    email=email,
                    emp_id=emp_id,
                    location=location,
                    building=building,
                    seat_no=seat_no,
                    contact_no=contact_no,
                    request_no=request_no,
                    department=department,
                    manager=manager,
                    project_specific=project_specific,
                    laptop_category=laptop_category,
                    other_assets=other_assets,
                    short_term=short_term,
                    manufacturer=manufacturer,
                    processor=processor,
                    adapter=adapter,
                    asset_tag_number=asset_tag_number,
                    ram_size=ram_size,
                    mouse=mouse,
                    serial_number=serial_number,
                    model=model,
                    hard_disk=hard_disk,
                    bag=bag,
                    battery_sl=battery_sl,
                    other_description=other_description,
                    confirmed=False,  # Default confirmation status
                )

                # Mark laptop as allocated
                laptop.allocation_status = "Allocated"
                laptop.save(update_fields=["allocation_status"])  # ✅ Ensures only status is updated

                print("✅ Allocation Saved:", allocation)

                send_allocation_email(allocation)

                messages.success(request, "Laptop allocated successfully! Email sent for confirmation.")
                return redirect("new_allocation")

            except Inventory.DoesNotExist:
                print("❌ Laptop Not Found in Inventory!")
                messages.error(request, "Selected laptop does not exist!")

    return render(request, "accounts/new_allocation.html", {
        "available_laptops": available_laptops,
        "allocated_laptops": allocated_laptops,
    })


# Send Confirmation Email
def send_allocation_email(allocation):
    allocation_url = f"http://127.0.0.1:8000/confirm-receipt/{allocation.id}/"

    subject = "Laptop Allocation Confirmation Required"
    message = f"""
Dear {allocation.engineer_name},

You have been allocated a laptop with the following details:

- **Asset Host Name:** {allocation.laptop.asset_host_name}
- **Allocation Date:** {allocation.allocation_date}

Please confirm the receipt of this laptop by clicking the link below:

{allocation_url}

Regards,  
IT Team
"""

    try:
        send_mail(
            subject,
            message,
            "sharathpatil333@gmail.com",
            [allocation.email],  # ✅ Correct recipient email
            fail_silently=False,
        )
        print("📩 Allocation email sent successfully!")
    except Exception as e:
        print("❌ Failed to send email:", str(e))  # ✅ Debugging

# Confirmation Page (User clicks URL)
@login_required
def confirm_receipt(request, id):
    allocation = get_object_or_404(Allocation, id=id)  # ✅ Fetch allocation

    if request.method == "POST":
        # Update allocation status
        allocation.confirmed = True
        allocation.save(update_fields=["confirmed"])

        # Email details
        subject = "Asset Receipt Confirmed"
        message = f"Hello,\n\nThe asset with ID {allocation.laptop.id} has been confirmed.\n\nRegards,\nIT Team"
        
        sender_email = allocation.email  # ✅ Fetch sender email from Allocation table
        receiver_email = "sharathpatil333@gmail.com"  # ✅ Fixed receiver email
        
        try:
            # Use Django's EmailMessage for better control
            email = email(
                subject=subject,
                body=message,
                from_email=sender_email,  # ✅ Dynamic sender (may not work with all SMTPs)
                to=[receiver_email],  # ✅ Receiver
            )
            email.send(fail_silently=False)
            print("📩 Confirmation email sent successfully!")

        except Exception as e:
            print(f"❌ Failed to send email: {str(e)}")  # ✅ Debugging
            messages.error(request, f"Failed to send email: {str(e)}")  # ✅ User feedback

        messages.success(request, "Asset receipt confirmed successfully!")

    return render(request, "accounts/confirmation.html", {"allocation": allocation})

def export_allocations_to_excel(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="allocations.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Engineer Name", "Email", "Laptop", "Allocated On", "Confirmed", "User Confirmation Name",
        "Emp ID", "Location", "Building", "Seat No", "Contact No", "Request No",
        "Department", "Manager", "Project", "Laptop Category", "Other Assets",
        "Short Term", "Manufacturer", "Processor", "Adapter", "Asset Tag", "RAM Size",
        "Mouse", "Serial No", "Model", "Hard Disk", "Bag", "Battery SL", "Other Description"
    ])

    allocations = Allocation.objects.all()
    for allocation in allocations:
        writer.writerow([
            allocation.engineer_name, allocation.email, allocation.laptop.asset_host_name, allocation.allocated_on,
            allocation.confirmed, allocation.user_confirmation_name, allocation.emp_id, allocation.location,
            allocation.building, allocation.seat_no, allocation.contact_no, allocation.request_no,
            allocation.department, allocation.manager, allocation.project_specific,
            allocation.laptop_category, allocation.other_assets, allocation.short_term,
            allocation.manufacturer, allocation.processor, allocation.adapter, allocation.asset_tag_number,
            allocation.ram_size, allocation.mouse, allocation.serial_number, allocation.model,
            allocation.hard_disk, allocation.bag, allocation.battery_sl, allocation.other_description
        ])

    return response

def generate_pdf(request, allocation_id):
    allocation = get_object_or_404(Allocation, id=allocation_id)

    # Load the HTML template
    template = get_template('accounts/confirmation.html')
    html_content = template.render({'allocation': allocation})

    # Define the file path
    pdf_path = os.path.join(settings.MEDIA_ROOT, f'Asset_Declaration_{allocation_id}.pdf')

    # Generate PDF
    HTML(string=html_content).write_pdf(pdf_path)

    # Serve the PDF file
    with open(pdf_path, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Asset_Declaration_{allocation_id}.pdf"'
        return response

'''-----------------------------------------------------------useless-------------------------------------------------------------------------------'''
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Inventory, Allocation

'''-----------------------------------------------------------------FAULTY ASSET REPLACEMENT---------------------------------------------------------------------------------------------------------------------------'''

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

'''------------------------------------------------------------------------DEALLOCATION---------------------------------------------------------------------------'''
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Inventory, Allocation, Deallocation

@login_required
def asset_deallocation(request):
    allocated_assets = Allocation.objects.all()  # Fetch allocated assets
    deallocated_assets = Deallocation.objects.all()  # Fetch deallocated assets

    if request.method == "POST":
        laptop_id = request.POST.get("laptop_id")
        data_transferred = request.POST.get("data_transferred") == "yes"

        laptop = get_object_or_404(Inventory, id=laptop_id)
        allocation = get_object_or_404(Allocation, laptop=laptop)

        if data_transferred:
            formatted = request.POST.get("formatted") == "yes"

            # Update Inventory
            laptop.allocation_status = "Deallocated"
            laptop.license_status = "Pending"
            laptop.installed_apps = ""  # Clear installed apps
            laptop.save()

            # Save to Deallocation Table
            Deallocation.objects.create(
                laptop=laptop,
                engineer_name=allocation.engineer_name,
                email=allocation.email,
                data_transferred=True,
                formatted=formatted,
            )

            # Remove from Allocation Table
            allocation.delete()

        return redirect("asset_deallocation")

    return render(request, "accounts/asset_deallocation.html", {
        "allocated_assets": allocated_assets,
        "deallocated_assets": deallocated_assets,  # Pass to template
    })


