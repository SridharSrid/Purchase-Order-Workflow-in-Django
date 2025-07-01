from django.db import models
from django.contrib.auth.models import User

# 1. Supplier
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return self.name

# 2. Product
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock_quantity = models.IntegerField(default=0)
    reorder_threshold = models.IntegerField(default=10)  # Optional field for managing stock levels

    def reorder_needed(self):
        return self.stock_quantity < self.reorder_threshold

    def check_reorder_status(self):
        if self.stock < self.reorder_threshold:
            self.reorder_needed = True
        else:
            self.reorder_needed = False
        self.save()
        
    def __str__(self):
        return self.name

# 3. Purchase Order
class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Received', 'Received'),
    ]
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PO #{self.id} - {self.supplier.name}"

# 4. Purchase Order Items
class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ordered_quantity = models.IntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.ordered_quantity}"

# 5. Inventory Transactions
class InventoryTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPE_CHOICES)
    related_po = models.ForeignKey(PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True)
    transaction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.product.name} ({self.quantity})"
