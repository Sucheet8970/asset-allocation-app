from django import forms
from .models import Laptop, Inventory, APPLICATION_CHOICES

class LaptopForm(forms.ModelForm):
    class Meta:
        model = Laptop
        fields = ["asset_host_name", "installed_apps", "installation_status", "license_status"]

class InventoryForm(forms.ModelForm):
    installed_apps = forms.MultipleChoiceField(
        choices=APPLICATION_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Inventory
        fields = ['asset_host_name', 'installed_apps', 'installation_status', 'license_status']