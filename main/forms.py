from django import forms
from .models import Product, RatingAnswer

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

