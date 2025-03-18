from django.urls import path
from . import views

urlpatterns = [
    # Главная страница
    path('', views.index_view, name='index'),

    # Продукт
    path('product/<int:product_id>/', views.product_detail_view, name='product_detail'),
    path('product/create/', views.product_create_view, name='product_create'),
    path('product/update/<int:product_id>/', views.product_update_view, name='product_update'),
    path('catalog/', views.product_list_view, name='catalog'),

    # Рейтинг
    path('rating/create/<int:product_id>/', views.rating_create_view, name='rating_create'),
    path('rating-answer/create/<int:rating_id>/', views.rating_answer_create_view, name='rating_answer_create'),

    # Профиль
    path('profile/', views.profile_view, name='profile'),
    path('download-receipt/<int:order_id>/', views.download_receipt, name='download_receipt'),


    # корзина и оплата
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment-method/create/', views.payment_method_create_view, name='payment_method_create'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),

]
