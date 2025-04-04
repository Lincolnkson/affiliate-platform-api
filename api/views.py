from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .models import (
    User, Vendor, VendorCategory, Affiliate, Product, ProductCategory, Review
)
from .serializers import (
    UserSerializer, RegisterSerializer, VendorSerializer, VendorRegisterSerializer,
    AffiliateSerializer, AffiliateRegisterSerializer, ProductSerializer,
    ProductCreateSerializer, CategorySerializer, ReviewSerializer
)
from .permissions import (
    IsVendor, IsAffiliate, IsAdmin, IsProductOwner, IsReviewAuthor
)

# Custom token auth view
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'account_type': user.account_type
        })

# Authentication views
class RegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class RegisterVendorView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = VendorRegisterSerializer

class RegisterAffiliateView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = AffiliateRegisterSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user

# Vendor views
class VendorViewSet(viewsets.ModelViewSet):
    serializer_class = VendorSerializer
    
    def get_queryset(self):
        if self.request.user.account_type == 'admin':
            return Vendor.objects.all()
        elif self.request.user.account_type == 'vendor' and hasattr(self.request.user, 'vendor_profile'):
            return Vendor.objects.filter(id=self.request.user.vendor_profile.id)
        return Vendor.objects.none()
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsVendor | IsAdmin]
        return super().get_permissions()
    
    @action(detail=True, methods=['get'], url_path='products')
    def get_vendor_products(self, request, pk=None):
        vendor = self.get_object()
        products = vendor.products.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

# # Product views
# class ProductViewSet(viewsets.ModelViewSet):
#     queryset = Product.objects.all()
    
#     def get_serializer_class(self):
#         if self.action == 'create':
#             return ProductCreateSerializer
#         return ProductSerializer
    
#     def get_permissions(self):
#         if self.action in ['list', 'retrieve']:
#             self.permission_classes = [AllowAny]
#         elif self.action == 'create':
#             self.permission_classes = [IsVendor]
#         else:
#             self.permission_classes = [IsProductOwner | IsAdmin]
#         return super().get_permissions()
    
#     @action(detail=True, methods=['post'])
#     def add_category(self, request, pk=None):
#         product = self.get_object()
#         serializer = CategorySerializer(data=request.data)
        
#         if serializer.is_valid():
#             category = serializer.validated_data['category']
#             if not ProductCategory.objects.filter(product=product, category=category).exists():
#                 ProductCategory.objects.create(product=product, category=category)
#                 return Response({"message": "Category added"}, status=status.HTTP_201_CREATED)
#             return Response({"message": "Category already exists"}, status=status.HTTP_400_BAD_REQUEST)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Product views

from rest_framework.generics import RetrieveUpdateAPIView, DestroyAPIView

# Add these views to your existing views.py
class ProductPartialUpdateView(RetrieveUpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsProductOwner | IsAdmin]
    http_method_names = ['get', 'patch']  # Only allow GET and PATCH

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class ProductDeleteView(DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsProductOwner | IsAdmin]
    http_method_names = ['delete']  # Only allow DELETE
    
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProductCreateSerializer
        return ProductSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [AllowAny]
        elif self.action == 'create':
            self.permission_classes = [IsVendor]
        elif self.action in ['update', 'partial_update', 'destroy']:  # Explicitly include all modification actions
            self.permission_classes = [IsProductOwner | IsAdmin]
        else:
            self.permission_classes = [IsAuthenticated]  # Default for any other actions
        return super().get_permissions()
    
    # Add explicit partial_update handler if you need custom behavior
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    # Add explicit destroy handler if you need custom behavior
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    

    
    @action(detail=True, methods=['post'])
    def add_category(self, request, pk=None):
        product = self.get_object()
        serializer = CategorySerializer(data=request.data)
        
        if serializer.is_valid():
            category = serializer.validated_data['category']
            if not ProductCategory.objects.filter(product=product, category=category).exists():
                ProductCategory.objects.create(product=product, category=category)
                return Response({"message": "Category added"}, status=status.HTTP_201_CREATED)
            return Response({"message": "Category already exists"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Review views
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    
    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return Review.objects.filter(product_id=product_id)
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [AllowAny]
        elif self.action == 'create':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsReviewAuthor | IsAdmin]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        serializer.save(product=product, user=self.request.user)

# Affiliate views
class AffiliateViewSet(viewsets.ModelViewSet):
    serializer_class = AffiliateSerializer
    
    def get_queryset(self):
        if self.request.user.account_type == 'admin':
            return Affiliate.objects.all()
        elif self.request.user.account_type == 'affiliate' and hasattr(self.request.user, 'affiliate_profile'):
            return Affiliate.objects.filter(id=self.request.user.affiliate_profile.id)
        return Affiliate.objects.none()
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAffiliate | IsAdmin]
        return super().get_permissions()