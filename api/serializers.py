from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Vendor, VendorCategory, Affiliate, Product, ProductCategory, Review

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'account_type', 'first_name', 'last_name', 'contact_number', 'status')
        read_only_fields = ('id',)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'account_type', 'first_name', 'last_name')
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Password fields don't match."})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)

class VendorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Vendor
        fields = ('id', 'user', 'company_name')

class VendorRegisterSerializer(serializers.ModelSerializer):
    user = RegisterSerializer()
    
    class Meta:
        model = Vendor
        fields = ('user', 'company_name')
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['account_type'] = 'vendor'
        user = RegisterSerializer().create(user_data)
        vendor = Vendor.objects.create(user=user, **validated_data)
        return vendor

class AffiliateSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Affiliate
        fields = ('id', 'user', 'affiliate_code', 'total_earnings')

class AffiliateRegisterSerializer(serializers.ModelSerializer):
    user = RegisterSerializer()
    
    class Meta:
        model = Affiliate
        fields = ('user', 'affiliate_code')
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['account_type'] = 'affiliate'
        user = RegisterSerializer().create(user_data)
        affiliate = Affiliate.objects.create(user=user, **validated_data)
        return affiliate

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ('category',)

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = ('id', 'user', 'rating', 'text', 'created_at')
        read_only_fields = ('id', 'created_at')

class ProductSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ('id', 'vendor', 'name', 'description', 'price', 'status', 'created_at', 'categories', 'reviews')
        read_only_fields = ('id', 'created_at')

class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('name', 'description', 'price', 'status')
    
    def create(self, validated_data):
        user = self.context['request'].user
        if hasattr(user, 'vendor_profile'):
            vendor = user.vendor_profile
            product = Product.objects.create(vendor=vendor, **validated_data)
            return product
        raise serializers.ValidationError("User is not a vendor")