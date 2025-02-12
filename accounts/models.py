from django.db import models
from datetime import date

APPLICATION_CHOICES = [
    ('Sophos Antivirus', 'Sophos Antivirus'),
    ('Patch Manager', 'Patch Manager'),
    ('SASE Proxy Agent', 'SASE Proxy Agent'),
    ('Summit', 'Summit'),
]

class Laptop(models.Model):
    asset_host_name = models.CharField(max_length=100, unique=True)
    installed_apps = models.TextField(blank=True, null=True)
    installation_status = models.BooleanField(default=False)
    license_status = models.CharField(max_length=50, default="Pending", null=False, blank=False)
    allocation_status = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=[('available', 'Available'), ('allocated', 'Allocated'), ('faulty', 'Faulty')], default='available')  
    received_from_left_employee = models.BooleanField(default=False)  
    faulty_status = models.BooleanField(default=False)  
    replacement_reason = models.TextField(blank=True, null=True)  

    def __str__(self):
        return self.asset_host_name


class Inventory(models.Model):
    asset_host_name = models.CharField(max_length=100, unique=True)
    installed_apps = models.JSONField(default=list)  
    allocation_status = models.CharField(max_length=50, default="Available")
    replaced_with = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="replaced_asset")

    # Individual License Statuses
    sophos_status = models.CharField(max_length=10, default="Pending", choices=[("Pending", "Pending"), ("Confirmed", "Confirmed")])
    patch_manager_status = models.CharField(max_length=10, default="Pending", choices=[("Pending", "Pending"), ("Confirmed", "Confirmed")])
    sase_proxy_status = models.CharField(max_length=10, default="Pending", choices=[("Pending", "Pending"), ("Confirmed", "Confirmed")])
    summit_status = models.CharField(max_length=10, default="Pending", choices=[("Pending", "Pending"), ("Confirmed", "Confirmed")])

    license_status = models.CharField(max_length=10, default="Pending", choices=[("Pending", "Pending"), ("Active", "Active")])

    def __str__(self):
        return self.asset_host_name


class Allocation(models.Model):
    laptop = models.OneToOneField(Inventory, on_delete=models.CASCADE)  # One laptop per engineer
    engineer_name = models.CharField(max_length=100)
    email = models.EmailField()
    allocated_on = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)  
    allocation_date = models.DateField(default=date.today)

    def __str__(self):
        return f"{self.engineer_name} - {self.laptop.asset_host_name}"


# ➤ **NEW: Deallocation Model**
class Deallocation(models.Model):
    laptop = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    engineer_name = models.CharField(max_length=100)
    email = models.EmailField()
    deallocation_date = models.DateTimeField(auto_now_add=True)
    data_transferred = models.BooleanField(default=False)
    formatted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.laptop.asset_host_name} - Deallocated"
