from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.utils.translation import gettext_lazy as _
from .models import (
    User, Vendor, VendorProductCategory, Affiliate, AffiliateReferralLink,
    Admin, Product, ProductCategory, ProductImage, ProductColor, Review
)

class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'account_type', 'first_name', 'last_name', 'status')
    list_filter = ('account_type', 'status', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'contact_number', 'profile_image')}),
        ('Account info', {'fields': ('account_type', 'status')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'account_type'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

admin.site.register(User, UserAdmin)
admin.site.register(Vendor)
admin.site.register(VendorProductCategory)
admin.site.register(Affiliate)
admin.site.register(AffiliateReferralLink)
admin.site.register(Admin)
admin.site.register(Product)
admin.site.register(ProductCategory)
admin.site.register(ProductImage)
admin.site.register(ProductColor)
admin.site.register(Review)