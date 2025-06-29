from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group

# Create PO
class PurchaseOrderCreateView(generics.CreateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

# List and Filter POs
class PurchaseOrderListView(generics.ListAPIView):
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        status = self.request.query_params.get('status')
        if status:
            return PurchaseOrder.objects.filter(status=status)
        return PurchaseOrder.objects.all()

# Delete a PO (only if Pending)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_po(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if po.status != 'Pending':
        return Response({"error": "Only Pending orders can be deleted."}, status=400)
    po.delete()
    return Response({"message": "Purchase Order deleted."})

# Approve a PO (Only Managers)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_po(request, pk):
    if not request.user.groups.filter(name='Manager').exists():
        return Response({"error": "Only Managers can approve."}, status=403)

    po = get_object_or_404(PurchaseOrder, pk=pk)
    po.status = 'Approved'
    po.save()
    return Response({"message": "Purchase Order approved."})

# Receive Goods from a PO
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def receive_po(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    all_received = True
    partial = False

    for item in po.items.all():
        qty = request.data.get(str(item.id))  # expect item-wise quantity
        if qty:
            qty = int(qty)
            item.received_quantity += qty
            item.save()

            # Update inventory
            item.product.stock_quantity += qty
            item.product.save()
            InventoryTransaction.objects.create(
                product=item.product,
                quantity_changed=qty,
                transaction_type='Received from PO'
            )

            if item.received_quantity < item.ordered_quantity:
                all_received = False
                partial = True

    if all_received:
        po.status = 'Completed'
    elif partial:
        po.status = 'Partially Delivered'
    po.save()
    return Response({"message": "Goods received and inventory updated."})
