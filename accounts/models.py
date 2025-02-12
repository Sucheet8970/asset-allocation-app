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
    installed_apps = models.JSONField(default=list)  # ✅ Consistent format
    installation_status = models.BooleanField(default=False)
    license_status = models.CharField(max_length=50, choices=[("Pending", "Pending"), ("Active", "Active")], default="Pending")
    allocation_status = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=[('available', 'Available'), ('allocated', 'Allocated'), ('faulty', 'Faulty')], default='available')
    received_from_left_employee = models.BooleanField(default=False)
    faulty_status = models.BooleanField(default=False)
    replacement_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.asset_host_name

class Inventory(models.Model):
    asset_host_name = models.CharField(max_length=100, unique=True)
    installed_apps = models.JSONField(default=list)  # ✅ Fixed default value
    allocation_status = models.CharField(max_length=50, choices=[("Available", "Available"), ("Allocated", "Allocated")], default="Available")
    last_assigned_engineer = models.CharField(max_length=100, blank=True, null=True)  # ✅ Track last engineer
    data_transfer_status = models.CharField(max_length=20, choices=[("Pending", "Pending"), ("Completed", "Completed")], default="Pending")
    replaced_with = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="replaced_asset")

    # License Status Fields
    sophos_status = models.CharField(max_length=10, default="Pending", choices=[("Pending", "Pending"), ("Confirmed", "Confirmed")])
    patch_manager_status = models.CharField(max_length=10, default="Pending", choices=[("Pending", "Pending"), ("Confirmed", "Confirmed")])
    sase_proxy_status = models.CharField(max_length=10, default="Pending", choices=[("Pending", "Pending"), ("Confirmed", "Confirmed")])
    summit_status = models.CharField(max_length=10, default="Pending", choices=[("Pending", "Pending"), ("Confirmed", "Confirmed")])
    license_status = models.CharField(max_length=10, default="Pending", choices=[("Pending", "Pending"), ("Active", "Active")])

    def deallocate(self):
        """ Mark laptop as deallocated and update inventory """
        self.allocation_status = "Available"
        self.data_transfer_status = "Pending"
        self.save()

    def __str__(self):
        return self.asset_host_name

class Allocation(models.Model):
    laptop = models.OneToOneField(Inventory, on_delete=models.CASCADE)
    engineer_name = models.CharField(max_length=100)
    email = models.EmailField()
    allocated_on = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)
    allocation_date = models.DateField(default=date.today)

    def deallocate_laptop(self):
        """ Deallocate the laptop and update inventory """
        self.laptop.allocation_status = "Available"
        self.laptop.last_assigned_engineer = self.engineer_name
        self.laptop.save()
        self.delete()

    def __str__(self):
        return f"{self.engineer_name} - {self.laptop.asset_host_name}"
