from django import forms
from ecommerce.models import Order


class OrderForm(forms.ModelForm):
    """
    Form for making orders. Based on Order model.
    Defines basic contact information about a customer.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in (field for field in iter(self.fields) if field != 'payment_option'):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta:
        """
        Binds form to respective Order model.
        """
        model = Order
        fields = ['name', 'email', 'phone', 'city', 'payment_option']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'js-masked-phone', 'placeholder': '+7 (999) 000 00 00'}),
            'city': forms.TextInput(attrs={'placeholder': 'Санкт-Петербург'}),
            'payment_option': forms.RadioSelect()
        }