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

# @login_required
# def dashboard(request):
#     return render(request, 'dashboard.html')
def login_page(request):
    return render(request, 'login.html')

def custom_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Group-based redirection
            if user.groups.filter(name='Manager').exists():
                return redirect('manager-dashboard')
            elif user.groups.filter(name='Employee').exists():
                return redirect('create-po')
            else:
                return redirect('create-po')  # default
        else:
            messages.error(request, 'Invalid username or password.')  # Add message for error

    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


class CustomAuthToken(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        print("CustomAuthToken POST called")
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        groups = list(user.groups.values_list('name', flat=True))

        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'groups': groups
        })

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

            return redirect('purchase_order_success')  # Create this success page or redirect to PO list
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


@login_required
def purchase_order_list(request):
    purchase_orders = PurchaseOrder.objects.all()
    return render(request, 'purchase_order_list.html', {'purchase_orders': purchase_orders})

# @login_required
# def approve_po(request, pk):
#     po = get_object_or_404(PurchaseOrder, pk=pk)
#     if request.user.groups.filter(name="manager").exists():
#         po.status = 'Approved'
#         po.save()
#     return redirect('purchase-orders')

# @login_required
# def reject_po(request, pk):
#     po = get_object_or_404(PurchaseOrder, pk=pk)
#     if request.user.groups.filter(name="manager").exists():
#         po.status = 'Rejected'
#         po.save()
#     return redirect('purchase-orders')
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    return Response({
        'username': request.user.username,
        'groups': list(request.user.groups.values_list('name', flat=True))
    })
