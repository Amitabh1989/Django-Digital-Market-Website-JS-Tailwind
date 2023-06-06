from django.urls import path
from .views import (
    AppHomeView, ProductListView, ProductDetailView,
    SuccessView, PaymentFailedView, CheckoutView, ProductFormView,
    ProductUpdateView, EditSuccessView, DeleteProductView,
    DeleteSuccessView, DashboardView, UserRegistrationView
    )
from django.contrib.auth import views as auth_views

app_name = "myapp"

# URLS : myapp/
urlpatterns = [
    path("", AppHomeView.as_view(), name="app_home"),
    path("product_list/", ProductListView.as_view(), name='product_list'),
    path("product_detail/<int:pk>", ProductDetailView.as_view(), name='product_detail'),
    path("success/", SuccessView.as_view(), name='success'),
    path("failed/", PaymentFailedView.as_view(), name='failed'),
    path("api/checkout/<int:pk>", CheckoutView.as_view(), name="api_session"),
    path("create_product/", ProductFormView.as_view(), name="create_product"),
    path("product_update/<int:pk>", ProductUpdateView.as_view(), name='product_update'),
    path("edit_success/", EditSuccessView.as_view(), name='edit_success'),
    path("delete_product/<int:pk>", DeleteProductView.as_view(), name='delete_product'),
    path("delete_success/", DeleteSuccessView.as_view(), name='delete_success'),
    path("dashboard/", DashboardView.as_view(), name='dashboard'),
    path("register/", UserRegistrationView.as_view(), name='register'),
    path("login/", auth_views.LoginView.as_view(template_name='myapp/login.html'), name='login'),
    # path("logout/", auth_views.LogoutView.as_view(template_name='myapp/logout.html'), name='logout'),
]
