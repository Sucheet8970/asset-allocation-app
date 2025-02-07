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
    license_status = models.BooleanField(default=False)
    allocation_status = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=[('available', 'Available'), ('allocated', 'Allocated'), ('faulty', 'Faulty')], default='available')  
    received_from_left_employee = models.BooleanField(default=False)  
    faulty_status = models.BooleanField(default=False)  # New field for faulty tracking
    replacement_reason = models.TextField(blank=True, null=True)  # Reason for replacement
    

    def __str__(self):
        return self.asset_host_name



class Inventory(models.Model):
    asset_host_name = models.CharField(max_length=100, unique=True)
    installed_apps = models.JSONField(default=list)  # ✅ Set default value
    license_status = models.CharField(max_length=50, default="Pending")
    allocation_status = models.CharField(max_length=50, default="Available")
    replaced_with = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="replaced_asset")


    def __str__(self):
        return self.asset_host_name
    
class Allocation(models.Model):
    laptop = models.OneToOneField(Inventory, on_delete=models.CASCADE)  # One laptop per engineer
    engineer_name = models.CharField(max_length=100)
    email = models.EmailField()
    allocated_on = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)  # If allocation is confirmed
    allocation_date = models.DateField(default=date.today)

    def __str__(self):
        return f"{self.engineer_name} - {self.laptop.asset_host_name}"

