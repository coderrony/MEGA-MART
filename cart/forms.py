from orders.models import Order
from django import forms


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address_line_1',
                  'address_line_2', 'country', 'state', 'city', 'order_note']
        widgets = {
            'order_note': forms.Textarea(attrs={'class': 'form-control', 'cols': '30', 'rows': '10'})
        }

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {'class': 'form-control'})
