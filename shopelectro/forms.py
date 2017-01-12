from django import forms
from django.forms import NumberInput, TextInput, Textarea

from shopelectro.models import Order, Product


class OrderForm(forms.ModelForm):
    """
    Form for making orders. Based on Order model.
    Define required contact information about a customer.
    """
    class Meta:
        model = Order
        input_css_class = 'form-control'

        fields = [
            'name', 'email', 'phone', 'city',
            'address', 'payment_type'
        ]

        widgets = {
            'name': TextInput(attrs={'class': input_css_class}),
            'email': TextInput(attrs={'class': input_css_class}),
            'phone': TextInput(attrs={'class': input_css_class}),
            'city': TextInput(attrs={
                'class': input_css_class,
                'placeholder': 'Санкт - Петербург'
            }),
            'address': Textarea(attrs={
                'class': input_css_class,
                'rows': 5,
            }),
            'payment_type': forms.RadioSelect(),
        }


class AddProductForm(forms.ModelForm):
    """Form for adding new Product in Table Editor."""

    class Meta:
        model = Product
        fields = [
            'name',
            'category',
            'price',
            'wholesale_small',
            'wholesale_medium',
            'wholesale_large'
        ]

        widgets = {
            'name': TextInput(
                attrs={
                    'class': 'form-control js-required',
                    'data-id': 'name',
                    'id': 'entity-name',
                }),
            'category': TextInput(
                attrs={
                    'class': 'form-control js-required',
                    'data-id': 'category',
                    'id': 'entity-category',
                }),
            'price': NumberInput(
                attrs={
                    'class': 'form-control js-required',
                    'data-id': 'price',
                    'id': 'entity-price',
                    'max': '1000000.00',
                    'min': '0.00',
                    'pattern': '[0-9]',
                    'step': '1.00'
                }),
            'wholesale_small': NumberInput(
                attrs={
                    'class': 'form-control js-required',
                    'data-id': 'wholesale_small',
                    'id': 'entity-wholesale-small',
                    'max': '1000000.00',
                    'min': '0.00',
                    'pattern': '[0-9]',
                    'step': '1.00'
                }),
            'wholesale_medium': NumberInput(
                attrs={
                    'class': 'form-control js-required',
                    'data-id': 'wholesale_medium',
                    'id': 'entity-wholesale-medium',
                    'max': '1000000.00',
                    'min': '0.00',
                    'pattern': '[0-9]',
                    'step': '1.00'
                }),
            'wholesale_large': NumberInput(
                attrs={
                    'class': 'form-control js-required',
                    'data-id': 'wholesale_large',
                    'id': 'entity-wholesale-large',
                    'max': '1000000.00',
                    'min': '0.00',
                    'pattern': '[0-9]',
                    'step': '1.00'
                })
        }
