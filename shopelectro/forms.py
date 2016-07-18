from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    """
    Form for making orders. Based on Order model.
    Define required contact information about a customer.
    """
    class Meta:
        model = Order
        fields = ['name', 'email', 'phone', 'city', 'payment_option']
        widgets = {
            'payment_option': forms.RadioSelect()
        }