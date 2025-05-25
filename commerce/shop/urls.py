from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/user/", views.user_dashboard, name="user_dashboard"),
    path("products/", views.product_list, name="product_list"),
    path("products/add/", views.add_product, name="add_product"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.view_cart, name="view_cart"),
    path(
        "cart/update/<int:item_id>/<str:action>/",
        views.update_cart_item,
        name="update_cart_item",
    ),
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/success/", views.checkout_success, name="checkout_success"),
    path("write_review/<int:id>/", views.write_review, name="write_review"),
    path("dash_admin/", views.admin_dash, name="admin_dash"),
    # Order URLs
    path("orders/", views.a_order_list, name="admin_order_list"),
    path("orders/<int:order_id>/", views.a_order_detail, name="admin_order_detail"),
    path(
        "orders/<int:order_id>/update/",
        views.a_update_order_status,
        name="admin_update_order_status",
    ),
    # Product URLs
    path("admin-panel/products/", views.a_product_list, name="admin_product_list"),
    path(
        "admin-panel/products/<int:product_id>/",
        views.a_product_detail,
        name="admin_product_detail",
    ),
    # Review URLs
    path("reviews/", views.a_review_list, name="admin_review_list"),
    path("reviews/<int:review_id>/", views.a_review_detail, name="admin_review_detail"),
    # Discount URLs
    path("discounts/", views.a_discount_list, name="admin_discount_list"),
    # Transaction URLs
    path("transactions/", views.a_transaction_list, name="admin_transaction_list"),
    path("account/", views.account_view, name="account"),
    path("categories/", views.category_list, name="category_list"),
    path("faq/", views.faq, name="faq"),
    path("shipping-policy/", views.shipping_policy, name="shipping_policy"),
    path("return-policy/", views.return_policy, name="return_policy"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("terms-conditions/", views.terms_conditions, name="terms_conditions"),
]
