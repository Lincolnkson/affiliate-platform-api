from django.shortcuts import render
from rest_framework import viewsets
from .serializers import (
    UserSerializer, UserRegistrationSerializer, VendorCategorySerializer,
    VendorSerializer, VendorRegistrationSerializer, AffiliateReferralLinkSerializer,
    AffiliateSerializer, AffiliateRegistrationSerializer, AdminSerializer,
    AdminRegistrationSerializer, ProductCategorySerializer, ProductColorSerializer,
    ProductImageSerializer, ReviewSerializer, ProductSerializer, ProductCreateSerializer
)
from .models import (
    UserManager, User, Vendor, VendorProductCategory, Affiliate,
    AffiliateReferralLink, Admin, Product, ProductCategory,
    ProductImage, ProductColor, Review
)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer