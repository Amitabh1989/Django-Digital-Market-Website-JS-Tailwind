from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Product(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    price = models.FloatField()
    file = models.FileField(upload_to='uploads')
    total_sales_amount = models.IntegerField(default=0)
    total_sales = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f'{self.name}'
    

class Order(models.Model):
    customer_email = models.EmailField()
    products = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField()
    stripe_payment_intent = models.CharField(max_length=200)
    has_pad = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.products}'