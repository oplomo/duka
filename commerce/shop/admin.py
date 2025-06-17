from django.contrib import admin
from .models import Product, ProductImage, Order, Review, Discount
from .utils import generate_review_hash

# ------------------------
# Inline for Product Images
# ------------------------


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text")
    readonly_fields = ("id",)


# ------------------------
# Product Admin
# ------------------------


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "seller", "price", "stock", "created_at")
    list_filter = ("category", "created_at")
    search_fields = ("name", "description", "seller__username")
    inlines = [ProductImageInline]


# ------------------------
# Order Admin
# ------------------------


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "buyer",
        "product",
        "quantity",
        "is_delivered",
        "reviewed",
        "created_at",
    )
    list_filter = ("is_delivered", "created_at")
    search_fields = ("buyer__username", "product__name")


# ------------------------
# Discount Admin
# ------------------------


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("code", "user", "percentage", "is_used", "created_at", "expires_at")
    list_filter = ("is_used", "created_at", "expires_at")
    search_fields = ("user__username", "code")


from .models import Product, ProductImage, Order, Review, Discount, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


# ------------------------
# Review Admin
# ------------------------

from django.contrib import admin
from .models import Review
from .utils import generate_review_hash


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "reviewer", "order", "rating", "is_updated", "created_at")
    readonly_fields = ("created_at", "last_changed_hash")

    def save_model(self, request, obj, form, change):
        if change:
            obj.is_updated = True

        # Always generate signed_credential
        obj.signed_credential = generate_review_hash(obj)

        super().save_model(request, obj, form, change)
from .models import Color  # adjust path if needed

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex_code')  # shows name and hex in admin list
    search_fields = ('name', 'hex_code') 