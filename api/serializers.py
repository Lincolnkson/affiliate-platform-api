from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import (
    Vendor, VendorProductCategory, Affiliate, AffiliateReferralLink,
    Admin, Product, ProductCategory, ProductImage, ProductColor, Review
)

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'account_type', 'first_name', 'last_name', 
                  'profile_image', 'contact_number', 'status', 'created_at', 'last_login')
        read_only_fields = ('id', 'created_at', 'last_login')

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'account_type', 'first_name', 'last_name', 'contact_number')
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Password fields don't match."})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)

class VendorCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProductCategory
        fields = ('category',)

class VendorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    categories = VendorCategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Vendor
        fields = ('id', 'user', 'company_name', 'tax_id', 'account_number', 
                  'bank_name', 'swift_code', 'commission_rate', 'payout_threshold', 'categories')
        read_only_fields = ('id',)

class VendorRegistrationSerializer(serializers.ModelSerializer):
    user = UserRegistrationSerializer()
    
    class Meta:
        model = Vendor
        fields = ('user', 'company_name', 'tax_id', 'account_number', 
                  'bank_name', 'swift_code', 'commission_rate', 'payout_threshold')
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['account_type'] = 'vendor'
        user = UserRegistrationSerializer().create(user_data)
        vendor = Vendor.objects.create(user=user, **validated_data)
        return vendor

class AffiliateReferralLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = AffiliateReferralLink
        fields = ('referral_link',)

class AffiliateSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    referral_links = AffiliateReferralLinkSerializer(many=True, read_only=True)
    
    class Meta:
        model = Affiliate
        fields = ('id', 'user', 'affiliate_code', 'total_earnings', 'pending_earnings', 
                  'paid_earnings', 'click_through_rate', 'conversion_rate', 
                  'total_referrals', 'referral_links')
        read_only_fields = ('id', 'total_earnings', 'pending_earnings', 'paid_earnings', 
                           'click_through_rate', 'conversion_rate', 'total_referrals')

class AffiliateRegistrationSerializer(serializers.ModelSerializer):
    user = UserRegistrationSerializer()
    
    class Meta:
        model = Affiliate
        fields = ('user', 'affiliate_code')
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['account_type'] = 'affiliate'
        user = UserRegistrationSerializer().create(user_data)
        affiliate = Affiliate.objects.create(user=user, **validated_data)
        return affiliate

class AdminSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Admin
        fields = ('id', 'user', 'can_manage_users', 'can_manage_products', 
                 'can_process_payments', 'can_access_reports', 'access_level')
        read_only_fields = ('id',)

class AdminRegistrationSerializer(serializers.ModelSerializer):
    user = UserRegistrationSerializer()
    
    class Meta:
        model = Admin
        fields = ('user', 'can_manage_users', 'can_manage_products', 
                 'can_process_payments', 'can_access_reports', 'access_level')
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['account_type'] = 'admin'
        user = UserRegistrationSerializer().create(user_data)
        admin = Admin.objects.create(user=user, **validated_data)
        return admin

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ('category',)

class ProductColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductColor
        fields = ('color',)

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'url', 'alt_text', 'is_primary')
        read_only_fields = ('id',)

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = ('id', 'user', 'rating', 'text', 'created_at', 'verified_purchase')
        read_only_fields = ('id', 'created_at')

class ProductSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer(read_only=True)
    categories = ProductCategorySerializer(many=True, read_only=True)
    colors = ProductColorSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ('id', 'vendor', 'name', 'description', 'price_base', 'price_discounted', 
                  'currency', 'dimensions', 'weight', 'status', 'views', 'sales_count', 
                  'affiliate_commission_rate', 'created_at', 'updated_at', 'categories', 
                  'colors', 'images', 'reviews')
        read_only_fields = ('id', 'created_at', 'updated_at', 'views', 'sales_count')

class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('name', 'description', 'price_base', 'price_discounted', 
                  'currency', 'dimensions', 'weight', 'status', 'affiliate_commission_rate')
    
    def create(self, validated_data):
        user = self.context['request'].user
        if hasattr(user, 'vendor_profile'):
            vendor = user.vendor_profile
            product = Product.objects.create(vendor=vendor, **validated_data)
            return product
        raise serializers.ValidationError("User is not a vendor")