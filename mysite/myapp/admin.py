from django.contrib import admin
from .models import Product, Order

# Register your models here.

admin.site.site_header = "Nebula Admin"
admin.site.site_title = "Nebula Marketplace Admin"
admin.site.index_title = "Nebula Market"
admin.site.register(Product)
admin.site.register(Order)
