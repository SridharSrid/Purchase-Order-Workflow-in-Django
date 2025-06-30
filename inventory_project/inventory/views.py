# from django.shortcuts import render
# from rest_framework import generics, status
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.response import Response
# from .models import *
# from .serializers import *
# from rest_framework.permissions import IsAuthenticated
# from django.shortcuts import get_object_or_404
# from django.contrib.auth.models import Group
# from .models import PurchaseOrder, PurchaseOrderItem, Product
# from .serializers import PurchaseOrderSerializer

# # Create PO
# class PurchaseOrderCreateView(generics.CreateAPIView):
#     queryset = PurchaseOrder.objects.all()
#     serializer_class = PurchaseOrderSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         # serializer.save(created_by=self.request.user)
#          serializer.save(status='Pending', created_by=self.request.user)

# # List and Filter POs
# class PurchaseOrderListView(generics.ListAPIView):
#     serializer_class = PurchaseOrderSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         status = self.request.query_params.get('status')
#         if status:
#             return PurchaseOrder.objects.filter(status=status)
#         return PurchaseOrder.objects.all()

# # Delete a PO (only if Pending)
# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# def delete_po(request, pk):
#     po = get_object_or_404(PurchaseOrder, pk=pk)
#     if po.status != 'Pending':
#         return Response({"error": "Only Pending orders can be deleted."}, status=400)
#     po.delete()
#     return Response({"message": "Purchase Order deleted."})

# # Approve a PO (Only Managers)
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def approve_po(request, pk):
#     if not request.user.groups.filter(name='Manager').exists():
#         return Response({"error": "Only Managers can approve."}, status=403)

#     po = get_object_or_404(PurchaseOrder, pk=pk)
#     if po.status != 'Pending':
#        return Response({"error": "Only Pending POs can be approved."}, status=400)
#     po.status = 'Approved'
#     po.save()
#     return Response({"message": "Purchase Order approved."})

# # Receive Goods from a PO
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def receive_po(request, pk):
#     po = get_object_or_404(PurchaseOrder, pk=pk)
#     all_received = True
#     partial = False

#     for item in po.items.all():
#         qty = request.data.get(str(item.id))  # expect item-wise quantity
#         # if qty:
#         #     qty = int(qty)
#         if qty is None:
#             continue 
#         try:
#             qty = int(qty)
#         except ValueError:
#             return Response({"error": f"Invalid quantity for item {item.id}"}, status=400)

#         if qty < 0 or item.received_quantity + qty > item.ordered_quantity:
#             return Response({"error": f"Invalid quantity for item {item.id}"}, status=400)


#         item.received_quantity += qty
#         item.save()
#             # Update inventory
#         item.product.stock_quantity += qty
#         item.product.save()
#         InventoryTransaction.objects.create(
#              product=item.product,
#              quantity_changed=qty,
#              transaction_type='Received from PO'
#          )
#         if item.received_quantity < item.ordered_quantity:
#             all_received = False
#             partial = True

#     if all_received:
#         po.status = 'Completed'
#     elif partial:
#         po.status = 'Partially Delivered'
#     po.save()
#     return Response({"message": "Goods received and inventory updated."})

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def list_purchase_orders(request):
#     status_param = request.GET.get('status')
    
#     if status_param:
#         pos = PurchaseOrder.objects.filter(status=status_param)
#     else:
#         pos = PurchaseOrder.objects.all()
    
#     serializer = PurchaseOrderSerializer(pos, many=True)
#     return Response(serializer.data)




from django.shortcuts import get_object_or_404
from .serializers import PurchaseOrderSerializer
from django.contrib.auth.models import Group

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Product, Supplier, PurchaseOrder, InventoryTransaction
from .forms import SupplierForm
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

def list_purchase_orders(request):
    purchase_orders = PurchaseOrder.objects.select_related('supplier', 'product').all()
    return render(request, 'po_list.html', {'purchase_orders': purchase_orders})

def products_view(request):
    products = Product.objects.all()
    return render(request, 'inventory/products.html', {'products': products})

def suppliers_view(request):
    suppliers = Supplier.objects.all()
    return render(request, 'inventory/suppliers.html', {'suppliers': suppliers})

def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('suppliers')
    else:
        form = SupplierForm()
    return render(request, 'inventory/add_supplier.html', {'form': form})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_purchase_order(request, pk):
    if not request.user.groups.filter(name='Manager').exists():
        return Response({'detail': 'Only managers can approve purchase orders.'}, status=403)

    try:
        po = PurchaseOrder.objects.get(pk=pk)
    except PurchaseOrder.DoesNotExist:
        return Response({'detail': 'Purchase order not found.'}, status=404)

    if po.status == 'Approved':
        return Response({'detail': 'Purchase order is already approved.'}, status=400)

    po.status = 'Approved'
    po.save()
    return Response({'detail': 'Purchase order approved.'}, status=200)



def purchase_orders_view(request):
    pos = PurchaseOrder.objects.all()
    return render(request, 'inventory/purchase_orders.html', {'purchase_orders': pos})

class CreatePurchaseOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PurchaseOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # 'status' will be set to 'Pending' inside serializer
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



def inventory_view(request):
    transactions = InventoryTransaction.objects.all()
    return render(request, 'inventory/inventory_transactions.html', {'transactions': transactions})

# 1. Create Purchase Order
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def create_po(request):
#     serializer = PurchaseOrderSerializer(data=request.data)
#     if serializer.is_valid():
#         po = serializer.save(status='Pending')
#         return Response(PurchaseOrderSerializer(po).data, status=201)
#     return Response(serializer.errors, status=400)


# # 2. Approve Purchase Order (Manager Only)
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def approve_po(request, pk):
#     po = get_object_or_404(PurchaseOrder, pk=pk)
#     if po.status != 'Pending':
#         return Response({"error": "Only Pending POs can be approved."}, status=400)

#     # Check user is in 'Manager' group
#     if not request.user.groups.filter(name='Manager').exists():
#         return Response({"error": "Only Managers can approve POs."}, status=403)

#     po.status = 'Approved'
#     po.save()
#     return Response({"message": "Purchase Order approved."})


# # 3. Receive Goods from a PO
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def receive_goods(request, pk):
#     po = get_object_or_404(PurchaseOrder, pk=pk)
#     if po.status not in ['Approved', 'Partially Delivered']:
#         return Response({"error": "Only Approved or Partially Delivered POs can receive goods."}, status=400)

#     items = po.items.all()
#     all_received = True

#     for item in items:
#         received_qty = int(request.data.get(f'product_{item.product.id}_received', 0))
#         item.received_quantity += received_qty
#         item.save()

#         # Update inventory
#         item.product.stock += received_qty
#         item.product.save()

#         if item.received_quantity < item.quantity:
#             all_received = False

#     if all_received:
#         po.status = 'Completed'
#     else:
#         po.status = 'Partially Delivered'
#     po.save()

#     return Response({"message": "Goods received and inventory updated."})


# # 4. List Purchase Orders with optional status filter
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def list_pos(request):
#     status = request.GET.get('status')
#     if status:
#         pos = PurchaseOrder.objects.filter(status=status)
#     else:
#         pos = PurchaseOrder.objects.all()
#     serializer = PurchaseOrderSerializer(pos, many=True)
#     return Response(serializer.data)


# 5. Delete PO (only if status is Pending)
# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# def delete_po(request, pk):
#     po = get_object_or_404(PurchaseOrder, pk=pk)
#     if po.status != 'Pending':
#         return Response({"error": "Only Pending orders can be deleted."}, status=400)
#     po.delete()
#     return Response({"message": "Purchase Order deleted."})

# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# def delete_po(request, pk):
#     try:
#         po = PurchaseOrder.objects.get(pk=pk)
#         po.delete()
#         return Response({'message': f'Purchase Orderssss {pk} deleted.'}, status=status.HTTP_200_OK)
#     except PurchaseOrder.DoesNotExist:
#         return Response({'error': 'Purchase Order not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_po(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if po.status != 'Pending':
        return Response({"error": "Only Pending orders can be deleted."}, status=400)
    po.delete()
    return Response({"message": f"Purchase Order {pk} deleted."}, status=200)