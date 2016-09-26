from django import forms

from shopelectro.models import Order


class OrderForm(forms.ModelForm):
    """
    Form for making orders. Based on Order model.
    Define required contact information about a customer.
    """
    class Meta:
        model = Order
        fields = ['name', 'email', 'phone', 'city', 'payment_type']
        widgets = {
            'payment_type': forms.RadioSelect()
        }
