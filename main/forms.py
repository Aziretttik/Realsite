from django import forms
from .models import Product, PaymentMethod, Order

# формочка для создания продукта
class ProductCreateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = (
              'title',
              'category',
              'main_image',
              'images',
              'description',
              'price'
              )

# формочка для изменения продукта
class ProductUpdateForm(forms.ModelForm):
            class Meta:
                model = Product
                fields = (
                    'title',
                    'category',
                    'main_image',
                    'images',
                    'description',
                    'price'
                )

#формочка для создания способа оплаты
class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['title', 'qr_image']
        labels = {
            'title': 'Название',
            'qr_image': 'QR-код'
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'qr_image': forms.FileInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.user:
            count = PaymentMethod.objects.filter(user=self.user).count()
            if count >= 4:
                raise forms.ValidationError('У вас уже максимальное количество способов оплаты (4)')
        return cleaned_data


class PaymentProofForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['payment_proof']
        labels = {
            'payment_proof': 'Загрузить чек об оплате'
        }
        widgets = {
            'payment_proof': forms.FileInput(attrs={'class': 'form-control'})
        }

