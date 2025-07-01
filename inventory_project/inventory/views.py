from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import PurchaseOrderSerializer
from .models import Product, Supplier, PurchaseOrder, PurchaseOrderItem
from .forms import PurchaseOrderForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login


def custom_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Role-based redirection
            if user.groups.filter(name='Manager').exists():
                return redirect('manager_dashboard')
            elif user.groups.filter(name='Employee').exists():
                return redirect('purchase_order_create')
            else:
                messages.warning(request, "No role assigned.")
                return redirect('purchase_order_create')  # or error

        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})



def login_page(request):
    return render(request, 'login.html')
@login_required
def manager_dashboard(request):
    return render(request, 'manager_dashboard.html')

def create_po(request):
    return render(request, 'create_po.html')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_purchase_order(request):
    serializer = PurchaseOrderSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def create_purchase_order(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            supplier = form.cleaned_data['supplier']
            product = form.cleaned_data['product']
            qty = form.cleaned_data['ordered_quantity']
            price = form.cleaned_data['price_per_unit']

            po = PurchaseOrder.objects.create(supplier=supplier, created_by=request.user)
            PurchaseOrderItem.objects.create(purchase_order=po, product=product, ordered_quantity=qty, price_per_unit=price)
            print("sssssssssssss")
            return redirect('purchase-order-success')  # Create this success page or redirect to PO list
    else:
        form = PurchaseOrderForm()

    return render(request, 'create_po.html', {'form': form})

def purchase_order_success(request):
    return render(request, 'purchase_order_success.html')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_purchase_order(request, pk):
    if not request.user.groups.filter(name='Manager').exists():
        return Response({'detail': 'Only managers can approve purchase orders.'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        po = PurchaseOrder.objects.get(pk=pk)
    except PurchaseOrder.DoesNotExist:
        return Response({'detail': 'Purchase order not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    po.status = 'Approved'
    po.save()
    return Response({'detail': 'Purchase order approved successfully.'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_purchase_order(request, pk):
    try:
        po = PurchaseOrder.objects.get(pk=pk)
    except PurchaseOrder.DoesNotExist:
        return Response({'detail': 'Purchase order not found.'}, status=status.HTTP_404_NOT_FOUND)

    if not request.user.groups.filter(name='Manager').exists():
        return Response({'detail': 'Only managers can reject purchase orders.'}, status=status.HTTP_403_FORBIDDEN)

    po.status = 'Rejected'
    po.save()
    return Response({'detail': 'Purchase order rejected successfully.'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_purchase_orders(request):
    pos = PurchaseOrder.objects.all()
    serializer = PurchaseOrderSerializer(pos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# @login_required
# def purchase_order_list(request):
#     purchase_orders = PurchaseOrder.objects.all()
#     return render(request, 'purchase_order_list.html', {'purchase_orders': purchase_orders})
def purchase_order_list(request):
    status = request.GET.get('status')
    if status:
        pos = PurchaseOrder.objects.filter(status=status)
    else:
        pos = PurchaseOrder.objects.all()
    return render(request, 'purchase_order_list.html', {'purchase_orders': pos})


@login_required
def approve_po(request, pk):
    if request.method == 'POST':
        po = get_object_or_404(PurchaseOrder, pk=pk)
        po.status = 'Approved'
        po.save()
        return redirect('manager_dashboard')

@login_required
def reject_po(request, pk):
    if request.method == 'POST':
        po = get_object_or_404(PurchaseOrder, pk=pk)
        po.status = 'Rejected'
        po.save()
        return redirect('manager_dashboard')

@login_required
def manager_dashboard(request):
    if not request.user.groups.filter(name='Manager').exists():
        return redirect('dashboard')  # Or return 403

    pending_pos = PurchaseOrder.objects.filter(status='Pending')
    return render(request, 'manager_dashboard.html', {'pending_pos': pending_pos})

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import PurchaseOrder, PurchaseOrderItem, InventoryTransaction

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def receive_goods(request, pk):
    try:
        po = PurchaseOrder.objects.get(pk=pk)
    except PurchaseOrder.DoesNotExist:
        return Response({"detail": "Purchase order not found."}, status=status.HTTP_404_NOT_FOUND)

    if po.status not in ['Approved', 'Partially Delivered']:
        return Response({"detail": "Only Approved or Partially Delivered POs can be received."}, status=status.HTTP_400_BAD_REQUEST)

    items_data = request.data.get('items', [])

    if not items_data:
        return Response({"detail": "No items provided for receiving."}, status=status.HTTP_400_BAD_REQUEST)

    all_received = True

    for item_data in items_data:
        item_id = item_data.get('item_id')
        qty_received = int(item_data.get('quantity_received', 0))

        try:
            item = PurchaseOrderItem.objects.get(id=item_id, purchase_order=po)
        except PurchaseOrderItem.DoesNotExist:
            continue

        # Update received quantity
        item.quantity_received += qty_received
        item.save()

        # Update stock
        item.product.stock += qty_received
        item.product.save()

        # Log inventory transaction
        InventoryTransaction.objects.create(
            product=item.product,
            quantity_changed=qty_received,
            note=f"Received via PO #{po.id}"
        )

        if item.quantity_received < item.quantity_ordered:
            all_received = False

    # Update PO status
    if all_received:
        po.status = 'Completed'
    else:
        po.status = 'Partially Delivered'
    po.save()

    return Response({"detail": "Goods received and inventory updated."})

def receive_goods_form(request, id):
    po = get_object_or_404(PurchaseOrder, id=id)
    if request.method == 'POST':
        # Handle the submitted received quantities here
        pass
    return render(request, 'receive_goods.html', {'po': po})


# Delete Purchase Order
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_purchase_order(request, pk):
    try:
        po = PurchaseOrder.objects.get(pk=pk)
        if po.status != 'Pending':
            return Response({'error': 'Only pending orders can be deleted.'}, status=status.HTTP_400_BAD_REQUEST)
        po.delete()
        return Response({'message': 'Purchase Order deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
    except PurchaseOrder.DoesNotExist:
        return Response({'error': 'Purchase Order not found.'}, status=status.HTTP_404_NOT_FOUND)

@login_required
def delete_purchase_order_ui(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    user_group = request.user.groups.first().name

    if po.status != 'Pending':
        messages.error(request, 'Only Pending orders can be deleted.')
        return redirect('purchase_order_list')

    if user_group not in ['Procurement Officer', 'Manager']:
        messages.error(request, 'You do not have permission to delete this.')
        return redirect('purchase_order_list')

    po.delete()
    messages.success(request, 'Purchase order deleted successfully.')
    return redirect('purchase_order_list')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_purchase_orders(request):
    print("API view hit") 
    status_filter = request.GET.get('status')
    
    if status_filter:
        pos = PurchaseOrder.objects.filter(status=status_filter)
    else:
        pos = PurchaseOrder.objects.all()
    
    serializer = PurchaseOrderSerializer(pos, many=True)
    return Response(serializer.data)


@login_required
def product_inventory_view(request):
    products = Product.objects.all()
    return render(request, 'product_inventory.html', {'products': products})
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def receive_purchase_order(request, pk):
    try:
        po = PurchaseOrder.objects.get(pk=pk)
    except PurchaseOrder.DoesNotExist:
        return Response({'detail': 'Purchase order not found.'}, status=status.HTTP_404_NOT_FOUND)

    if po.status not in ['Approved', 'Partially Delivered']:
        return Response({'detail': 'Only approved or partially delivered orders can be received.'},
                        status=status.HTTP_400_BAD_REQUEST)

    items_data = request.data.get('items', [])

    all_received = True
    for item_data in items_data:
        item = PurchaseOrderItem.objects.get(id=item_data['item_id'], purchase_order=po)
        qty_received = int(item_data['quantity_received'])

        item.received_quantity += qty_received
        item.save()

        # Update stock
        product = item.product
        product.stock += qty_received
        product.check_reorder_status() 

        # Log inventory transaction
        InventoryTransaction.objects.create(
            product=product,
            quantity=qty_received,
            transaction_type='RECEIVED',
            purchase_order=po
        )

        # Check delivery status
        if item.received_quantity < item.quantity:
            all_received = False

    # Update PO status
    if all_received:
        po.status = 'Completed'
    else:
        po.status = 'Partially Delivered'
    po.save()

    return Response({'detail': 'Goods received and inventory updated successfully.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    return Response({
        'username': request.user.username,
        'groups': list(request.user.groups.values_list('name', flat=True))
    })

