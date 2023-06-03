from django.urls import path
from .views import AppHomeView, ProductListView, ProductDetailView

app_name = "myapp"

# URLS : myapp/
urlpatterns = [
    path("", AppHomeView.as_view(), name="app_home"),
    path("product_list/", ProductListView.as_view(), name='product_list'),
    path("product_detail/<int:pk>", ProductDetailView.as_view(), name='product_detail'),
]
