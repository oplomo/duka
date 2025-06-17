from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
import uuid
from decimal import Decimal


from django.shortcuts import render
from django.db import models  # Add this import for models
from django.db.models import Q  # Add this for complex queries
from .models import Category, Product, Review  # Add your other model imports as well
import random


def home(request):
    # Get featured categories (first 4 categories)
    categories_with_items_and_images = Category.objects.filter(
        products__images__isnull=False
    ).distinct()
    featured_categories = random.sample(
        list(categories_with_items_and_images),
        min(4, categories_with_items_and_images.count()),
    )
    for category in featured_categories:
        # Get products with images under this category
        products_with_images = Product.objects.filter(
            category=category, images__isnull=False
        ).distinct()

        if products_with_images.exists():
            product = random.choice(list(products_with_images))
            # Pick a random image from that product
            category.random_image = random.choice(list(product.images.all()))
        else:
            category.random_image = None
    # Get best sellers (products with most orders)
    best_sellers = Product.objects.annotate(
        order_count=models.Count("orders")
    ).order_by("-order_count")[:8]
    for product in best_sellers:
        if product.images.exists():
            product.random_image = random.choice(list(product.images.all()))
        else:
            product.random_image = None
    # Get new arrivals (recently added products) - get at least 3 for carousel
    new_arrivals = Product.objects.order_by("-created_at")[:8]
    carousel_products = Product.objects.order_by("-created_at")[:6].prefetch_related(
        "images"
    )
    for product in new_arrivals:
        if product.images.exists():
            product.random_image = random.choice(list(product.images.all()))
        else:
            product.random_image = None

    # Get featured reviews (recent positive reviews)
    featured_reviews = Review.objects.filter(rating__gte=4).order_by("-created_at")[:3]

    # Search functionality
    query = request.GET.get("q", "")  # Get search query from request
    if query:
        # Filter products based on name, description, and category name
        products = Product.objects.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        )
    else:
        products = Product.objects.all()  # Return all products if no search query

    context = {
        "featured_categories": featured_categories,
        "best_sellers": best_sellers,
        "new_arrivals": new_arrivals,
        "featured_reviews": featured_reviews,
        "products": products,
        "query": query,
        "carousel_products": carousel_products,  # Add the carousel products
    }

    return render(request, "shop/index.html", context)


# Registration view
def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! You can now log in.")
            return redirect("login")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})


# Custom login redirect view based on roles
from django.urls import reverse


class CustomLoginView(LoginView):
    template_name = "registration/login.html"

    def get_redirect_url(self):
        user = self.request.user
        if user.is_staff:
            return reverse(
                "admin_dash"
            )  # Use reverse to get the URL for the admin dashboard
        return reverse(
            "home"
        )  # Use reverse to get the URL for the regular user dashboard


# Dashboard views
@login_required
def user_dashboard(request):
    return render(request, "shop/user_dashboard.html")


from django.shortcuts import render
from django.db.models import Q, Count
from .models import Product, ProductImage, Category, Order
from .utils import user_can_review
from django.db.models import Avg


def product_list(request):
    # Start with all products and prefetch related images
    products = Product.objects.prefetch_related("images").all()
    products_with_review_rights = []

    if request.user.is_authenticated:
        for product in products:
            if user_can_review(request.user, product):
                products_with_review_rights.append(product.id)

    # Get all categories for filtering
    categories = Category.objects.all()

    # ===== SEARCH FUNCTIONALITY =====
    search_query = request.GET.get("q", "").strip()
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(category__name__icontains=search_query)
        ).distinct()

    # ===== CATEGORY FILTER =====
    category_id = request.GET.get("category")
    if category_id:
        products = products.filter(category__id=category_id)

    # ===== SORTING FUNCTIONALITY =====
    sort_option = request.GET.get("sort", "featured")

    if sort_option == "price_asc":
        products = products.order_by("price")
    elif sort_option == "price_desc":
        products = products.order_by("-price")
    elif sort_option == "newest":
        products = products.order_by("-created_at")
    elif sort_option == "bestselling":
        # Annotate with sales count and order by it
        products = products.annotate(sales_count=Count("orders")).order_by(
            "-sales_count", "-created_at"
        )
    else:  # featured (default)
        # For featured, we might want some logic like:
        # - Featured products first
        # - Then by some other criteria
        # For simplicity, we'll use random order here
        products = products.order_by("?")

    # ===== LOW STOCK FILTER (optional) =====
    if "low_stock" in request.GET:
        products = products.filter(stock__lt=5)

    # Prepare context with all needed data
    context = {
        "products": products,
        "categories": categories,
        "current_category": int(category_id) if category_id else None,
        "search_query": search_query,
        "sort_option": sort_option,
        "products_with_review_rights": products_with_review_rights,
    }

    return render(request, "shop/product_list.html", context)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.text import slugify
from .models import Product, Category, ProductImage, Color
import uuid

@login_required
def add_product(request):
    if request.method == "POST":
        # Process form data
        name = request.POST.get("name")
        category_id = request.POST.get("category")
        description = request.POST.get("description")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        size = request.POST.get("size")
        color_ids = request.POST.getlist("colors")
        source = request.POST.get("source", "local")
        supplier_name = request.POST.get("supplier_name")
        supplier_contact = request.POST.get("supplier_contact")
        supplier_price = request.POST.get("supplier_price")
        aliexpress_url = request.POST.get("aliexpress_url")
        delivery_fee = request.POST.get('delivery_fee') or 0

        images = request.FILES.getlist("images")



        # Validate required fields
        if not all([name, description, price, stock]):
            return render(
                request,
                "products/add_product.html",
                {
                    "error": "Please fill in all required fields",
                    "categories": Category.objects.all(),
                    "colors": Color.objects.all(),
                    "preserved_data": request.POST,
                },
            )

        try:
            with transaction.atomic():
                # Create the product
                product = Product(
                    seller=request.user,
                    name=name,
                    description=description,
                    price=price,
                    stock=stock,
                    size=size,
                    source=source,
                    supplier_name=supplier_name,
                    supplier_contact=supplier_contact,
                    aliexpress_url=aliexpress_url,
                    delivery_fee = delivery_fee
                )

                # Handle optional decimal field
                if supplier_price:
                    product.supplier_price = supplier_price

                if category_id:
                    product.category = Category.objects.get(id=category_id)

                product.save()

                # Add colors
                if color_ids:
                    product.color_options.set(Color.objects.filter(id__in=color_ids))

                # Save multiple images
                for image in images:
                    ProductImage.objects.create(product=product, image=image)
                
                return redirect("product_list")

        except Exception as e:
            return render(
                request,
                "shop/add_product.html",
                {
                    "error": f"An error occurred: {str(e)}",
                    "categories": Category.objects.all(),
                    "colors": Color.objects.all(),
                    "preserved_data": request.POST,
                },
            )

    # GET request - show empty form
    return render(
        request, 
        "shop/add_product.html", 
        {
            "categories": Category.objects.all(),
            "colors": Color.objects.all(),
            "source_choices": Product.SOURCE_CHOICES,
        }
    )

from django.shortcuts import render, get_object_or_404
from .models import Product


def product_detail(request, pk):
    product = get_object_or_404(Product.objects.prefetch_related("images"), pk=pk)
    products_with_review_rights = []
    reviews = Review.objects.filter(order__product=product)
    review_change_message = ""

    # Only check review rights for authenticated users
    if request.user.is_authenticated and user_can_review(request.user, product):
        products_with_review_rights.append(product.id)

    # Get related products (excluding current product)

    for review in reviews:
        if review.is_updated:
            review_change_message = (
                "This review has been updated. Please check it again."
            )

    related_products = (
        Product.objects.filter(category=product.category)
        .exclude(pk=product.pk)
        .prefetch_related("images")[:4]
    )

    context = {
        "product": product,
        "related_products": related_products,
        "products_with_review_rights": products_with_review_rights,
        "reviews": reviews,
        "review_change_message": review_change_message,
    }
    return render(request, "shop/product_detail.html", context)


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Cart, CartItem, Product


def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to add items to your cart.")
        return redirect("login")  # Replace with your login URL

    product = get_object_or_404(Product, id=product_id)

    # Get or create active cart for the user
    cart, created = Cart.objects.get_or_create(
        user=request.user, is_active=True, defaults={"user": request.user}
    )

    # Check if product is already in cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, defaults={"quantity": 1}
    )

    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"Added another {product.name} to your cart.")
        else:
            messages.warning(
                request,
                f"Cannot add more {product.name} - only {product.stock} available.",
            )
    else:
        messages.success(request, f"Added {product.name} to your cart.")

    return redirect("product_list")  # Or wherever you want to redirect


# views.py
from django.contrib import messages
from .models import Cart


def view_cart(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to view your cart.")
        return redirect("login")  # Replace with your login URL

    # Get the user's active cart
    cart = Cart.objects.filter(user=request.user, is_active=True).first()

    # Calculate the subtotal and total price after discount
    subtotal = cart.subtotal()  # Get the cart subtotal
    discount_amount = cart.apply_discount()  # Get the discount amount
    total_price = subtotal - discount_amount  # Calculate the total price to pay

    context = {
        "cart": cart,
        "subtotal": subtotal,
        "discount_amount": discount_amount,
        "total_price": total_price,
    }
    return render(request, "shop/view_cart.html", context)


def update_cart_item(request, item_id, action):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to update your cart.")
        return redirect("login")

    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if action == "increase":
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"Updated quantity for {cart_item.product.name}.")
        else:
            messages.warning(
                request,
                f"Cannot add more {cart_item.product.name} - only {cart_item.product.stock} available.",
            )
    elif action == "decrease":
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.success(request, f"Updated quantity for {cart_item.product.name}.")
        else:
            cart_item.delete()
            messages.success(
                request, f"Removed {cart_item.product.name} from your cart."
            )
    elif action == "remove":
        cart_item.delete()
        messages.success(request, f"Removed {cart_item.product.name} from your cart.")

    return redirect("view_cart")


from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cart, CartItem, Order, Discount
from .models import MPesaTransaction  # If you have an MpesaTransaction model
from django_daraja.mpesa.core import MpesaClient
import random
import string


import random
import string
from shop.models import MPesaTransaction  # Import your model here


def generate_transaction_code(length=10):
    """Generate a unique fake transaction code."""
    letters_and_digits = string.ascii_uppercase + string.digits

    while True:
        code = "".join(random.choice(letters_and_digits) for _ in range(length))
        if not MPesaTransaction.objects.filter(transaction_code=code).exists():
            return code


@transaction.atomic
def checkout(request):
    if not request.user.is_authenticated:
        return redirect("login")

    cart = get_object_or_404(Cart, user=request.user, is_active=True)
    cart_items = cart.items.all()

    # Calculate the discount and total amount to be paid
    discount_amount = 0
    discount = Discount.objects.filter(user=request.user, is_used=False).first()
    if discount and discount.is_eligible_for_discount():  # Apply discount if eligible
        discount_amount = cart.subtotal() * (
            Decimal(discount.percentage) / Decimal(100)
        )
        discount.is_used = True  # Mark the discount as used
        discount.save()  # Save discount state

    total_amount = cart.subtotal() - discount_amount  # Calculate total after discount

    if request.method == "POST":
        phone_number = request.POST.get("phone_number")
        if (
            not phone_number
            or not phone_number.isdigit()
            or not phone_number.startswith("254")
        ):
            messages.error(request, "Invalid phone number. Use format 2547XXXXXXXX")
            return redirect("checkout")

        # Proceed with MPesa payment
        mpesa_client = MpesaClient()

        try:
            # Initiate Mpesa STK Push
            response = mpesa_client.stk_push(
                phone_number,
                int(total_amount),
                account_reference="ShopEase",
                transaction_desc="Payment for Order",
                callback_url="https://darajambili.herokuapp.com/express-payment",
            )
            transaction_id = response.checkout_request_id
        except Exception as e:
            # If Mpesa call fails, still proceed but with a fake transaction id
            transaction_id = generate_transaction_code()
            messages.error(
                request,
                "Mpesa Payment initiation failed. We are processing your order.",
            )

        # Save Order(s)
        for item in cart_items:
            order = Order.objects.create(
                buyer=request.user,
                product=item.product,
                quantity=item.quantity,
                is_delivered=False,
                reviewed=False,
            )

            # Save MPesaTransaction immediately
            MPesaTransaction.objects.create(
                transaction_id=transaction_id,
                order=order,
                amount=total_amount,
                phone_number=phone_number,
                status="Pending",
            )

        messages.success(request, "Order placed successfully!")

        # Clear Cart
        cart.is_active = False
        cart.save()

        # Create a fresh cart for user
        Cart.objects.create(user=request.user)

        return redirect("checkout_success")

    return render(
        request,
        "shop/checkout.html",
        {
            "cart": cart,
            "total_amount": total_amount,
            "discount_amount": discount_amount,
        },
    )


def checkout_success(request):
    return render(request, "shop/checkout_success.html")


# views.py
import hashlib
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from .models import Product, Review, Order
from .forms import ReviewForm
from .utils import (
    user_can_review,
    create_or_update_review,
)  # Make sure the import is correct

def write_review(request, id):
    product = get_object_or_404(Product, pk=id)

    if not user_can_review(request.user, product):
        return HttpResponseForbidden("You are not allowed to review this product.")

    order = Order.objects.filter(
        buyer=request.user, product=product, is_delivered=True, reviewed=False
    ).first()

    if not order:
        return HttpResponseForbidden("You cannot review this product.")

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            rating = form.cleaned_data["rating"]
            comment = form.cleaned_data["comment"]
            review = create_or_update_review(order, rating, comment, request.user)

            order.reviewed = True
            order.save()

            if user_is_eligible_for_discount(request.user):
                create_discount_for_user(request.user)

            return redirect("product_detail", pk=product.pk)
        else:
            # Add this for debugging
            print("Form errors:", form.errors)
    else:
        form = ReviewForm()

    return render(
        request,
        "shop/write_review.html",
        {
            "product": product,
            "form": form,
        },
    )
def user_is_eligible_for_discount(user):
    # Check if the user has written reviews (can be extended with other conditions)
    return user.reviews.exists()


def create_discount_for_user(user):
    # Create a new discount for the user
    discount_code = str(uuid.uuid4())[:12]  # Generate a unique discount code
    discount = Discount.objects.create(
        user=user,
        code=discount_code,
        percentage=20,  # Set your desired discount percentage here
        is_used=False,
    )

    print(
        f"Discount of {discount.percentage}% created for {user.username} with code {discount.code}."
    )


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .models import Order, Product, Review, Category, Discount, MPesaTransaction


def is_admin(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(is_admin)
def admin_dash(request):
    # Get statistics for the dashboard
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(is_delivered=False).count()
    total_products = Product.objects.count()
    pending_reviews = Review.objects.filter(rating__isnull=True).count()

    recent_orders = Order.objects.order_by("-created_at")[:5]
    recent_transactions = MPesaTransaction.objects.order_by("-created_at")[:5]

    context = {
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "total_products": total_products,
        "pending_reviews": pending_reviews,
        "recent_orders": recent_orders,
        "recent_transactions": recent_transactions,
    }
    return render(request, "admin/dashboard.html", context)


@user_passes_test(is_admin)
def a_order_list(request):
    orders = Order.objects.all().order_by("-created_at")
    return render(request, "admin/orders/list.html", {"orders": orders})


@user_passes_test(is_admin)
def a_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "admin/orders/detail.html", {"order": order})


@user_passes_test(is_admin)
def a_update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        is_delivered = request.POST.get("is_delivered") == "on"
        order.is_delivered = is_delivered
        order.save()
        messages.success(request, f"Order #{order.id} status updated successfully.")
        return redirect("admin_order_detail", order_id=order.id)
    return redirect("admin_order_detail", order_id=order.id)


@user_passes_test(is_admin)
def a_product_list(request):
    products = Product.objects.all().order_by("-created_at")
    return render(request, "admin/products/list.html", {"products": products})


@user_passes_test(is_admin)
def a_product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "admin/products/detail.html", {"product": product})


@user_passes_test(is_admin)
def a_review_list(request):
    reviews = Review.objects.all().order_by("-created_at")
    return render(request, "admin/reviews/list.html", {"reviews": reviews})


@user_passes_test(is_admin)
def a_review_detail(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    return render(request, "admin/reviews/detail.html", {"review": review})


@user_passes_test(is_admin)
def a_discount_list(request):
    discounts = Discount.objects.all().order_by("-created_at")
    return render(request, "admin/discounts/list.html", {"discounts": discounts})


@user_passes_test(is_admin)
def a_transaction_list(request):
    transactions = MPesaTransaction.objects.all().order_by("-created_at")
    return render(
        request, "admin/transactions/list.html", {"transactions": transactions}
    )


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order, Review, Discount, Cart


@login_required
def account_view(request):
    user = request.user

    # Get user's orders
    orders = Order.objects.filter(buyer=user).order_by("-created_at")[:5]

    # Get user's reviews
    reviews = Review.objects.filter(reviewer=user).order_by("-created_at")[:5]

    # Get user's active discounts
    active_discounts = Discount.objects.filter(user=user, is_used=False).order_by(
        "-created_at"
    )

    # Get user's active cart
    try:
        cart = Cart.objects.get(user=user, is_active=True)
        cart_items = cart.items.all()
    except Cart.DoesNotExist:
        cart = None
        cart_items = None

    context = {
        "user": user,
        "orders": orders,
        "reviews": reviews,
        "active_discounts": active_discounts,
        "cart": cart,
        "cart_items": cart_items,
    }
    return render(request, "shop/account.html", context)


from django.shortcuts import render
from .models import Category, Product


from random import choice


def category_list(request):
    categories = Category.objects.all().prefetch_related("products__images")

    for category in categories:
        for product in category.products.all():
            if product.images.exists():
                product.random_image = choice(list(product.images.all()))
            else:
                product.random_image = None

    context = {"categories": categories}
    return render(request, "shop/categories.html", context)


def faq(request):
    return render(request, "shop/faq.html")


def shipping_policy(request):
    return render(request, "shop/shipping_policy.html")


def return_policy(request):
    return render(request, "shop/return_policy.html")


def privacy_policy(request):
    return render(request, "shop/privacy_policy.html")


def terms_conditions(request):
    return render(request, "shop/terms_conditions.html")
