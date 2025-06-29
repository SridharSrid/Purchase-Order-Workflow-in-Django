from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    stock_quantity = models.IntegerField(default=0)
    reorder_threshold = models.IntegerField(default=10)

    def reorder_needed(self):
        return self.stock_quantity < self.reorder_threshold

class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Partially Delivered', 'Partially Delivered'),
        ('Completed', 'Completed'),
    ]
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ordered_quantity = models.IntegerField()
    received_quantity = models.IntegerField(default=0)

class InventoryTransaction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_changed = models.IntegerField()
    transaction_type = models.CharField(max_length=50)  # e.g., 'Received from PO'
    transaction_date = models.DateTimeField(auto_now_add=True)
