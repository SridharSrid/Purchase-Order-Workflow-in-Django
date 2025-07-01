from django import forms
from .models import Supplier, Product

class PurchaseOrderForm(forms.Form):
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.all())
    product = forms.ModelChoiceField(queryset=Product.objects.all())
    ordered_quantity = forms.IntegerField(min_value=1)
    price_per_unit = forms.DecimalField(decimal_places=2, max_digits=10)

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_email', 'phone_number']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'unit_price', 'stock_quantity', 'reorder_threshold']