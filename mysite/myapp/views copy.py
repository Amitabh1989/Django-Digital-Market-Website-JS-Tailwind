from typing import Any, Dict
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.core.paginator import Paginator
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.conf import settings
from django.http import JsonResponse
from .models import Product, Order

import stripe
import json
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

    
    def post(self, request, *args, **kwargs):
        product = self.get_object()
        request_data = json.load(request.body)
        stripe.api_key = settings.STRIPE_SECRET_KEY

        success_url = request.build_absolute_uri(reverse('success')) + "?session_id={CHECKOUT_SESSION_ID}"
        # failure_url = request.build_absolute_uri(reverse('failed')) + "?session_id={CHECKOUT_SESSION_ID}"
        failure_url = request.build_absolute_uri(reverse('failed'))
        checkout_session = stripe.checkout.Session.create(
            customer_email = request_data['email'],
            payment_method_types = ['card'],
            line_items = [{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product.name,
                    },
                    'unit_amount': int(product.price * 100),
                },
                'quantity': 1,
            }],
            mode = 'payment',
            success_url = success_url,
            cancel_url = failure_url,  # request.build_absolute_uri(reverse('failed')),
        )

        # If the charge is successful, you can perform any necessary actions here
        # For example, update the order status, send a confirmation email, etc.

        # # Save order in the database
        # order = Order()
        # order.customer_email = request_data['email']
        # order.products = product
        # order.stripe_payment_intent = checkout_session["payment_intent"]
        # order.amount = int(product.price)
        # order.save()

        return JsonResponse({"session_id": checkout_session.id})


class SuccessView(TemplateView):
    template_name = "success.html"

    def get(self, request, *args, **kwargs):
        session_id = request.GET.get("session_id")

        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Retrieve the corresponding checkout session object from the stripe data
        try:
            checkout_session = stripe.checkout.Session.retrieve(session_id)
        except stripe.error.InvalidRequestError:
            return self.handle_invalid_session()

        # Now validate and process the checkout session
        if self.validate_session(checkout_session):
            self.process_session(checkout_session)
            return self.render_to_response({})
        else:
            return self.handle_invalid_session(checkout_session)
        
    def validate_session(self, checkout_session):
        # All custom validations go here 
        checkout_session.has_paid = True
        return checkout_session.get('has_paid') == True

    def process_session(self, checkout_session):
        # Retrieve the corresponding product based on the Checkout Session
        product = get_object_or_404(Product, name=checkout_session.get('products')[0].get('name'))

        # Save order in the database
        order = Order()
        order.customer_email = checkout_session.get('customer_details').get('email')
        order.products = product
        order.stripe_payment_intent = checkout_session.get("payment_intent")
        order.amount = int(product.price)
        order.save()
    
    def handle_invalid_session(self, checkout_session):
        # Handle invalid or failed sessions
        # For example, display an error message or redirect to an error page
        order = Order.objects.get(stripe_payment_intent=checkout_session.get('payment_intent'))
        context = {
            'order': order,
            'error_message': 'Payment session failed. Please try again.',
        }
        return self.render_to_response(context)

class PaymentFailedView(View):
    # def get(self, request):
    #     # Handle payment failure logic
    #     # Retrieve relevant data, perform error handling, etc.
    #     order = Order.objects.get(stripe_payment_intent=failed_payment_intent)
    #     context = {
    #         'order': order,
    #         'error_message': 'Payment failed. Please try again.',
    #     }
    def get(self, request):
        context = {
            # 'order': order,
            'error_message': 'Payment failed. Please try again.',
        }
        return render(request, 'failed.html', context)