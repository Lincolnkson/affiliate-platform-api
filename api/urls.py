from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomAuthToken, RegisterView, RegisterVendorView, RegisterAffiliateView, 
    UserProfileView, VendorViewSet, ProductViewSet, ReviewViewSet, AffiliateViewSet
    
)

router = DefaultRouter()
router.register(r'vendors', VendorViewSet, basename='vendor')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'affiliates', AffiliateViewSet, basename='affiliate')

# Product reviews nested router
product_reviews_router = DefaultRouter()
product_reviews_router.register(r'reviews', ReviewViewSet, basename='product-reviews')

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/register/vendor/', RegisterVendorView.as_view(), name='register-vendor'),
    path('auth/register/affiliate/', RegisterAffiliateView.as_view(), name='register-affiliate'),
    path('auth/login/', CustomAuthToken.as_view(), name='login'),
    path('auth/profile/', UserProfileView.as_view(), name='profile'),
    
    # Product reviews
    path('products/<int:product_id>/', include(product_reviews_router.urls)),
    
    # Include the router URLs
    path('', include(router.urls)),
]