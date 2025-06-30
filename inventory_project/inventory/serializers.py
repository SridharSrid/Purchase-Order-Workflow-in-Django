from rest_framework import serializers
from .models import Supplier, Product, PurchaseOrder, PurchaseOrderItem

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

# class PurchaseOrderItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PurchaseOrderItem
#         fields = '__all__'

# class PurchaseOrderSerializer(serializers.ModelSerializer):
#     items = PurchaseOrderItemSerializer(many=True)

#     class Meta:
#         model = PurchaseOrder
#         fields = '__all__'

#     def create(self, validated_data):
#         items_data = validated_data.pop('items')
#         po = PurchaseOrder.objects.create(**validated_data)
#         for item_data in items_data:
#             PurchaseOrderItem.objects.create(purchase_order=po, **item_data)
#         return po



class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderItem
        fields = ['product', 'quantity', 'price_per_unit']

class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True)

    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        po = PurchaseOrder.objects.create(created_by=user, status='Pending', **validated_data)
        for item_data in items_data:
            PurchaseOrderItem.objects.create(purchase_order=po, **item_data)
        return po
    



