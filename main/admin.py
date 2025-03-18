from django.contrib import admin
from .models import Category, Product, Order, Rating, RatingAnswer, Image, PaymentMethod, Cart, CartItem, OrderItem

# регистрация всех моделек в админке сайта
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Rating)
admin.site.register(RatingAnswer)
admin.site.register(Image)
admin.site.register(PaymentMethod)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)

