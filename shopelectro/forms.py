from django import forms
from django.forms import TextInput, Textarea

from shopelectro.models import Order


class OrderForm(forms.ModelForm):
    """
    Form for making orders. Based on Order model.
    Define required contact information about a customer.
    """
    class Meta:
        model = Order
        inputs_css_class = 'form-control'

        fields = [
            'name', 'email', 'phone', 'city',
            'address', 'payment_type'
        ]

        widgets = {
            'name': TextInput(attrs={'class': inputs_css_class}),
            'email': TextInput(attrs={'class': inputs_css_class}),
            'phone': TextInput(attrs={'class': inputs_css_class}),
            'city': TextInput(attrs={'class': inputs_css_class}),
            'address': Textarea(attrs={'class': inputs_css_class}),
            'payment_type': forms.RadioSelect(),
        }
