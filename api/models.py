from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from datetime import datetime

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('account_type', 'admin')
        extra_fields.setdefault('status', 'active')
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ACCOUNT_TYPES = (
        ('vendor', 'Vendor'),
        ('affiliate', 'Affiliate'),
        ('admin', 'Admin'),
    )
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('pending', 'Pending'),
    )
    
    # Add related_name attributes to avoid clash with auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='api_user_set',
        related_query_name='api_user'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='api_user_set',
        related_query_name='api_user'
    )

    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    contact_number = models.CharField(max_length=20, null=True)
    status = models.CharField('status', max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(null=True)
    last_login = models.DateTimeField(null=True)
    is_staff = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['account_type']
    
    def __str__(self):
        return self.email

class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    swift_code = models.CharField(max_length=50, blank=True, null=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    payout_threshold = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    def __str__(self):
        return self.company_name or str(self.id)

class VendorProductCategory(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='categories')
    category = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('vendor', 'category')
    
    def __str__(self):
        return f"{self.vendor} - {self.category}"

class Affiliate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='affiliate_profile')
    affiliate_code = models.CharField(max_length=50, unique=True)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pending_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    click_through_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    total_referrals = models.IntegerField(default=0)
    
    def __str__(self):
        return self.affiliate_code

class AffiliateReferralLink(models.Model):
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE, related_name='referral_links')
    referral_link = models.CharField(max_length=255)
    
    class Meta:
        unique_together = ('affiliate', 'referral_link')
    
    def __str__(self):
        return self.referral_link

class Admin(models.Model):
    
    ACCESS_LEVELS = (
        ('superAdmin', 'Super Admin'),
        ('moderator', 'Moderator'),
        ('support', 'Support'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    can_manage_users = models.BooleanField(default=False)
    can_manage_products = models.BooleanField(default=False)
    can_process_payments = models.BooleanField(default=False)
    can_access_reports = models.BooleanField(default=False)
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVELS)
    
    def __str__(self):
        return f"{self.user.email} - {self.access_level}"

class Product(models.Model):
    STATUS_CHOICES = (
        ('in_stock', 'In Stock'),
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
    )
    

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=2000)
    price_base = models.DecimalField(max_digits=10, decimal_places=2)
    price_discounted = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=10)
    dimensions = models.CharField(max_length=100, blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    views = models.IntegerField(default=0, blank=True, null=True)
    sales_count = models.IntegerField(default=0, blank=True, null=True)
    affiliate_commission_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)
    
    def __str__(self):
        return self.name

class ProductCategory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='categories')
    category = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('product', 'category')
    
    def __str__(self):
        return f"{self.product.name} - {self.category}"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    url = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.product.name} - {'Primary' if self.is_primary else 'Secondary'}"

class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='colors')
    color = models.CharField(max_length=50)
    
    class Meta:
        unique_together = ('product', 'color')
    
    def __str__(self):
        return f"{self.product.name} - {self.color}"

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()
    text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_purchase = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.product.name} - {self.user.email} - {self.rating}"
    
    def save(self, *args, **kwargs):
        if self.rating < 1 or self.rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        super().save(*args, **kwargs)