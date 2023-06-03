from typing import Any, Dict
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.generic import TemplateView, ListView, DetailView
from .models import Product
from django.conf import settings
import stripe

# Create your views here.


class AppHomeView(TemplateView):
    template_name = 'myapp/index.html'


class ProductListView(ListView):
    model = Product
    queryset = Product.objects.order_by("name")
    context_object_name = "products"
    paginate_by = 4

    def get_queryset(self) -> QuerySet[Any]:
        query = self.request.GET.get('item_description')
        queryset = super().get_queryset()
        if query:
            queryset = queryset.filter(Q(description__icontains=query))
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        paginator = Paginator(context['object_list'], self.paginate_by)
        page = self.request.GET.get("page")
        products = paginator.get_page(page)
        context["product_list"] = products
        return context


class ProductDetailView(DetailView):
    model = Product

    STRIPE_SECRET_KEY = settings.STRIPE_SECRET_KEY
    stripe.api_key = settings.STRIPE_SECRET_KEY

    
    def post(self, request, *args, **kwargs):
        product = self.get_object()

        # Get the Stripe token from the request
        token = request.POST.get('stripeToken')

        try:
            # Create a charge using the Stripe API
            charge = stripe.Charge.create(
                amount=int(product.price * 100),  # Stripe requires the amount in cents
                currency='usd',
                source=token,
                description='Payment for product: {}'.format(product.name),
            )

            # If the charge is successful, you can perform any necessary actions here
            # For example, update the order status, send a confirmation email, etc.

            return redirect(reverse_lazy('myapp:success_url'))  # Redirect to a success page

        except stripe.error.CardError as e:
            # Handle card errors and display an error message to the user
            error_message = e.user_message
            return render(request, 'payment_error.html', {'error_message': error_message})

        except stripe.error.StripeError as e:
            # Handle other Stripe errors
            error_message = 'An error occurred while processing your payment. Please try again later.'
            return render(request, 'payment_error.html', {'error_message': error_message})