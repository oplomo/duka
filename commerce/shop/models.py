from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.db.models import Avg
import uuid
from decimal import Decimal

# -----------------------
# Categories
# -----------------------


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


# -----------------------
# Product and Media
# -----------------------


class Product(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=1)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"pk": self.pk})

    def average_rating(self):
        return (
            Review.objects.filter(order__product=self).aggregate(Avg("rating"))[
                "rating__avg"
            ]
            or 0
        )


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="product_images/")
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.product.name}"


# -----------------------
# Orders and Reviews
# -----------------------


class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="orders"
    )
    quantity = models.PositiveIntegerField(default=1)
    is_delivered = models.BooleanField(default=False)
    reviewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.buyer.username}"


class Review(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(
        choices=[(i, f"{i} Stars") for i in range(1, 6)], blank=True, null=True
    )
    comment = models.TextField()
    is_updated = models.BooleanField(default=False)
    signed_credential = models.TextField(
        help_text="VC in JSON format, signed", blank=True, null=True
    )
    last_changed_hash = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for Order #{self.order.id}"


# -----------------------
# Discounts / Rewards
# -----------------------


def default_expiry():
    # Assuming you want the discount to expire in 30 days
    from datetime import timedelta, datetime

    return datetime.now() + timedelta(days=30)


class Discount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="discounts")
    code = models.CharField(max_length=12, unique=True, default=uuid.uuid4)
    percentage = models.PositiveIntegerField(default=20)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expiry)

    def __str__(self):
        return f"{self.percentage}% for {self.user.username} ({'Used' if self.is_used else 'Active'})"

    def is_eligible_for_discount(self):
        return self.user.reviews.exists()  # Only eligible if the user has reviews

    def apply_discount(self, subtotal):
        discount_amount = subtotal * (self.percentage / 100)
        return discount_amount


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Cart #{self.id} for {self.user.username}"

    def total_items(self):
        return self.items.aggregate(total=models.Sum("quantity"))["total"] or 0

    def subtotal(self):
        return sum(item.product.price * item.quantity for item in self.items.all())

    def apply_discount(self):
        discount = Discount.objects.filter(
            user=self.user, is_used=False
        ).first()  # Get the first discount available for the user
        if (
            discount and discount.is_eligible_for_discount()
        ):  # Check if the user is eligible for discount
            discount_amount = self.subtotal() * (
                Decimal(discount.percentage) / Decimal(100)
            )  # Use self.subtotal()

            return discount_amount
        return 0  # No discount applied


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart #{self.cart.id}"

    def item_total(self):
        return self.product.price * self.quantity


class MPesaTransaction(models.Model):
    transaction_id = models.CharField(max_length=100)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="mpesa_transactions"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    status = models.CharField(
        max_length=20, default="Pending"
    )  # Pending, Completed, Failed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.status}"
