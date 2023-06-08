
from django import http
from django.db import models
from django.forms.models import BaseModelForm
from .forms import ProductForm, UserRegistrationForm
from django.contrib import messages
from typing import Any, Dict
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.core.paginator import Paginator
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from .models import Product, Order, Profile
from django.core.exceptions import PermissionDenied
from django.db.models import Sum, Count
from datetime import datetime, timedelta
from django.utils import timezone


import stripe
import json
# Create your views here.


class AppHomeView(TemplateView):
    """
    Homepage for the myapp
    """
    template_name = 'myapp/index.html'

    
class ProductFormView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'myapp/product_form.html'
    success_url = reverse_lazy('myapp:product_list')

    # Uncomment below line to use function based view
    # ==============================================================================
    # def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
    #     if request.method == "POST":
    #         print("in post method")
    #         # form = ProductForm(request.POST, request.FILES)
    #         form = ProductForm(request.POST, request.FILES)
    #         print(f"Form : {form}")
    #         print(f"Form : {form.__dict__}")
    #         # form.seller = self.request.user
    #         print(f"in post method {form.is_valid()}")
    #         if form.is_valid():
    #             print("in valid")
    #             form = form.save(commit=False)
    #             form.seller = self.request.user
    #             form.save()
    #             return redirect("myapp:product_list")
    #         else:
    #             print("Invalid form")
    
    def form_valid(self, form):
        form.instance.seller = self.request.user
        return super().form_valid(form)
 

class ProductListView(ListView):
    model = Product
    queryset = Product.objects.order_by("name")
    context_object_name = "products"
    paginate_by = 4

    def get_queryset(self) -> QuerySet[Product]:
        """
        Get the queryset of products based on the search query parameter.

        Returns:
            QuerySet: Filtered queryset of products.
        """
        query = self.request.GET.get('item_description')
        queryset = super().get_queryset()
        if query:
            queryset = queryset.filter(Q(description__icontains=query))
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Get the context data for the product list view.

        Returns:
            dict: Context data for the product list view.
        """
        context = super().get_context_data(**kwargs)
        paginator = Paginator(context['object_list'], self.paginate_by)
        page = self.request.GET.get("page")
        products = paginator.get_page(page)
        context["product_list"] = products
        return context


class ProductDetailView(DetailView):
    model = Product

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Get the context data for the product detail view.

        Returns:
            dict: Context data for the product detail view.
        """
        context = super().get_context_data(**kwargs)
        context['stripe_publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY
        context['product_id'] = self.object.pk
        return context


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    fields = '__all__'

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()
        if self.object.seller != self.request.user:
            return redirect(reverse("myapp:permission_denied"))
        return super().get(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse('myapp:edit_success') #, kwargs={'pk': self.kwargs['pk']})

class PermissionDenied(TemplateView):
    template_name = 'myapp/permission_denied.html'

class EditSuccessView(TemplateView):
    template_name = 'myapp/edit_success.html'

class DeleteProductView(LoginRequiredMixin, DeleteView):
    # print("Inside Delete View")
    model = Product
    success_url = reverse_lazy('myapp:delete_success')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.seller != self.request.user:
            return redirect(reverse("myapp:permission_denied"))
        return super().get(request, *args, **kwargs)
    
class DeleteSuccessView(TemplateView):
    # print("Inside Delete success View")
    template_name = 'myapp/delete_success.html'

class CheckoutView(LoginRequiredMixin, DetailView):
    model = Product
    STRIPE_SECRET_KEY = settings.STRIPE_SECRET_KEY

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Get the context data for the checkout view.

        Returns:
            dict: Context data for the checkout view.
        """
        context = super().get_context_data(**kwargs)
        # Add any additional context data for the checkout view
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle the POST request for the checkout view.

        Returns:
            JsonResponse: JSON response containing the checkout session ID.
        """
        product = self.get_object()
        request_data = json.loads(request.body)
        stripe.api_key = self.STRIPE_SECRET_KEY

        success_url = request.build_absolute_uri(reverse('myapp:success')) + \
              "?session_id={CHECKOUT_SESSION_ID}"
        failure_url = request.build_absolute_uri(reverse('myapp:failed'))
        checkout_session = stripe.checkout.Session.create(
            customer_email=request_data['email'],
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product.name,
                    },
                    'unit_amount': int(product.price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            client_reference_id=self.kwargs.get("pk"),
            success_url=success_url,
            cancel_url=failure_url,
        )

        return JsonResponse({"session_id": checkout_session.id})


class SuccessView(TemplateView):
    template_name = "myapp/success.html"

    def get(self, request, *args, **kwargs):
        """
        Handle the GET request for the success view.

        Returns:
            TemplateResponse: Template response for the success view.
        """
        session_id = request.GET.get("session_id")

        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            checkout_session = stripe.checkout.Session.retrieve(session_id)
        except stripe.error.InvalidRequestError:
            return self.handle_invalid_session()

        if self.validate_session(checkout_session):
            self.process_session(checkout_session)
            return self.render_to_response({
                "product": checkout_session["ordered_product_details"],
                "order": checkout_session["order_details"]
            })
        else:
            return self.handle_invalid_session(checkout_session)

    def validate_session(self, checkout_session) -> bool:
        """
        Validate the checkout session.

        Args:
            checkout_session (dict): Checkout session data.

        Returns:
            bool: True if the session is valid and payment was successful, False otherwise.
        """
        payment_status = checkout_session.get('payment_status')
        has_paid = payment_status == 'paid'
        checkout_session['has_paid'] = has_paid
        return has_paid

    def process_session(self, checkout_session):
        """
        Process the checkout session.

        Args:
            checkout_session (dict): Checkout session data.
        """
        product_id = checkout_session.get('client_reference_id')
        product = Product.objects.get(id=product_id)
        checkout_session["ordered_product_details"] = {
            "name": product.name,
            "price": product.price,
        }

        order = Order()
        order.customer_email = checkout_session.get('customer_details').get('email')
        order.products = product
        order.stripe_payment_intent = checkout_session.get("payment_intent")
        order.amount = int(product.price)
        order.has_pad = checkout_session['has_paid']
        # Updating Sales stats for a product
        product.total_sales_amount = product.total_sales_amount + int(product.price)
        product.total_sales += 1
        product.save()
        # Updating Sales stats for a product
        order.save()
        checkout_session["order_details"] = order

    def handle_invalid_session(self, checkout_session):
        """
        Handle an invalid checkout session.

        Args:
            checkout_session (dict): Checkout session data.

        Returns:
            TemplateResponse: Template response for handling invalid session.
        """
        order = Order.objects.get(stripe_payment_intent=checkout_session.get('payment_intent'))
        context = {
            'order': order,
            'error_message': 'Payment session failed. Please try again.',
        }
        return self.render_to_response(context)


class PaymentFailedView(TemplateView):
    template_name = 'myapp/failed.html'
    
    def get_context_data(self, **kwargs):
        """
        Get the context data for the payment failed view.

        Returns:
            dict: Context data for the payment failed view.
        """
        context = super().get_context_data(**kwargs)
        context['error_message'] = 'Payment failed. Please try again.'
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle the POST request for the payment failed view.

        Returns:
            HttpResponseRedirect: HTTP redirect response to the checkout view.
        """
        # Perform any necessary actions for retrying payment
        # For example, update the order status, send notification, etc.

        return redirect('myapp:checkout')


class DashboardView(LoginRequiredMixin, ListView):
    model = Product
    context_object_name = "product_list"
    template_name = "myapp/dashboard.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(seller=self.request.user)
        return queryset

class UserRegistrationView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'myapp/register.html'
    success_url = 'myapp/login.html'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        print(f"User password : {user.password}")
        user.save()
        return redirect(reverse('myapp:login'))

class UserProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'myapp/profile.html'
    context_object_name = "profile_info" 


class MyPurchaseView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'myapp/purchases.html'
    context_object_name = "products"

    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        queryset = queryset.filter(customer_email=self.request.user.email)
        print(f"Products by {self.request.user} are {queryset}")
        return queryset

class SalesView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "myapp/sales.html"
    context_object_name = "object_list"

    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        print(f"Queryset : {queryset}")
        queryset = queryset.filter(products__seller=self.request.user)
        total_sales = queryset.aggregate(Sum("amount"))

        start_date = timezone.now() - timedelta(days=30)
        quarter_date = timezone.now() - timedelta(days=90)
        weekly_date = timezone.now() - timedelta(days=7)
        
        last_30_days_data = queryset.filter(created_on__range=[start_date, timezone.now()])
        last_30_days_sales = last_30_days_data.aggregate(Sum("amount"))

        quarterly_data = queryset.filter(created_on__range=[quarter_date, timezone.now()])
        quarterly_sales = quarterly_data.aggregate(Sum("amount"))

        weekly_data = queryset.filter(created_on__range=[weekly_date, timezone.now()])
        weekly_sales = weekly_data.aggregate(Sum("amount"))
        
        monthly_sales_by_day = last_30_days_data.values("created_on__date").order_by("created_on__date").annotate(daily_sales=Sum('amount'))
        # monthly_sales_by_day = last_30_days_data.values("created_on__date").annotate(daily_sales=Sum('amount'))
        print(f"monthly_sales_by_day : {monthly_sales_by_day}")

        product_sales = queryset.values("products__name").order_by("products__name").annotate(sale_count=Count('products__name')).annotate(sales=Sum("amount"))
        print(f"product_sales : {product_sales}")
        
        product_sales1 = queryset.values("products__name").order_by("products__name").annotate(sale_count=Sum("amount"))
        print(f"product_sales1 : {product_sales1}")

        context = {
            "queryset": queryset,
            "total_sales": total_sales,
            "30day_sales": last_30_days_sales,
            "quarterly_sales": quarterly_sales,
            "weekly_sales" : weekly_sales,
            "monthly_sales_by_day": monthly_sales_by_day,
            "product_sales": product_sales
        }
        return context