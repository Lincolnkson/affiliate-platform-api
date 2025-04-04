from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Vendor, VendorCategory, Affiliate, Product, ProductCategory, Review

# User Admin
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'account_type', 'is_staff')
    list_filter = ('account_type', 'is_staff', 'status')  # Using fields that exist in our User model
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)  # Using email instead of username
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'contact_number')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Status', {'fields': ('account_type', 'status')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'account_type'),
        }),
    )

# Other Admin classes remain the same as the simple version
class VendorAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name')

class VendorCategoryAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'category')

class AffiliateAdmin(admin.ModelAdmin):
    list_display = ('user', 'affiliate_code')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'price')

class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'category')

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating')

# Register all models
admin.site.register(User, UserAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(VendorCategory, VendorCategoryAdmin)
admin.site.register(Affiliate, AffiliateAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Review, ReviewAdmin)