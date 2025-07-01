from django.contrib import admin
from .models import Product, Supplier, PurchaseOrder, PurchaseOrderItem, InventoryTransaction

admin.site.register(Product)
admin.site.register(Supplier)
admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderItem)
admin.site.register(InventoryTransaction)
