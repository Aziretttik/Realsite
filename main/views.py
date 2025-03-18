from django.http import Http404, FileResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg
from django.core.paginator import Paginator
from .filters import ProductListFilter
from .models import Product, Rating, RatingAnswer, Cart, CartItem, Order, PaymentMethod, OrderItem, Category
from .forms import ProductCreateForm, ProductUpdateForm, PaymentMethodForm
from django.contrib import messages


# Главная страница
def index_view(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'main/index.html', {'products': products})


# Продукт
def product_detail_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_update_form = ProductUpdateForm(instance=product)
    product_comments = Rating.objects.filter(product=product)
    rating_avg = product_comments.aggregate(Avg('count'))['count__avg']

    similar_products = Product.objects.filter(category=product.category).exclude(id=product.id)
    return render(
        request=request,
        template_name='main/product_detail.html',
        context={
            'product': product,
            'similar_products': similar_products,
            'product_update_form': product_update_form,
            'product_comments': product_comments,
            'rating_avg': rating_avg})


# Продукт
def product_create_view(request):
    if not request.user.is_authenticated:
        raise Http404

    if request.method == 'POST':
        form = ProductCreateForm(request.POST, request.FILES)
        if form.is_valid():
            product_object = form.save(commit=False)
            product_object.user = request.user
            product_object.save()
            messages.success(request, 'успешно создано')
            return redirect('index')

    form = ProductCreateForm()
    return render(request, 'main/product_create.html', {'form': form })


# Продукт
def product_update_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if not product.user == request.user:
        raise Http404

    if request.method == 'POST':
        form = ProductUpdateForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'успешно изменено')
            return redirect('product_detail, product_id')


# Рейтинг
def rating_create_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if not request.user.is_authenticated:
        messages.error(request, 'только авторизованнные')
        return redirect('product_detail', product_id)

    if request.method == "POST":
        comment = request.POST.get('comment', '')
        count = int(request.POST.get('count', ''))
        rating = Rating(
            user=request.user,
            product=product,
            count=count,
            comment=comment)
        rating.save()
        messages.success(request, 'Отзыв успешно отправлен')
    return redirect('product_detail', product_id)


# Рейтинг
def rating_answer_create_view(request, rating_id):
    rating = get_object_or_404(Rating, id=rating_id)

    if rating.product.user != request.user:
        messages.error(request, 'у вас нет доступа')
        return redirect('product_detail', rating.product.id)

    if request.method == 'POST':
        comment = request.POST.get('comment', '')
        rating_answer = RatingAnswer(
            user=request.user,
            rating=rating,
            comment=comment)
        rating_answer.save()
        messages.success(request, 'ответ на отзыв успешно отправлен')
        return redirect('product_detail', rating.product.id)
    return redirect('product_detail', rating.product.id)


# Профиль
def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    products = Product.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user) \
        .prefetch_related('orderitem_set', 'orderitem_set__product') \
        .order_by('-created_at')

    return render(request, 'main/profile.html', {
        'products': products,
        'user': request.user,
        'orders': orders,
        'products_count': products.count()  # Добавляем счетчик объявлений
    })




def order_detail_view(request, order_id):
    order = Order.objects.get(id=order_id)
    orderitems = OrderItem.objects.filter(order=order)

    context = {
        'order': order,
        'orderitems': orderitems,
    }
    return render(request, 'order_detail.html', context)


def download_receipt(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.payment_proof:
        response = FileResponse(order.payment_proof.open(), as_attachment=True)
        return response
    else:
        messages.error(request, 'Чек не найден')
        return redirect('profile')


# способ оплаты
@login_required
def payment_method_create_view(request):
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            payment_method = form.save(commit=False)
            payment_method.user = request.user
            payment_method.save()
            messages.success(request, 'Способ оплаты успешно добавлен')
            return redirect('profile')
    else:
        form = PaymentMethodForm(user=request.user)

    return render(request, 'main/payment_method_create.html', {'form': form})

# Просмотр корзины
@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart.html',{'cart': cart})


# Добавление товара в корзину
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    quantity = int(request.POST.get('quantity', 1))

    if quantity < 1:
        quantity = 1
    elif quantity > 10:
        quantity = 10

    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    if not item_created:
        cart_item.quantity += quantity
        if cart_item.quantity > 10:
            cart_item.quantity = 10
        cart_item.save()
        messages.success(request, 'Количество товара в корзине обновлено')
    else:
        messages.success(request, 'Товар успешно добавлен в корзину')

    return redirect('cart_view')


# Оформление заказа
@login_required
def checkout(request):
    try:
        cart = Cart.objects.get(user=request.user)  # Убрали is_active из фильтра
        payment_methods = PaymentMethod.objects.filter(user=request.user)

        if request.method == 'POST':
            payment_method_id = request.POST.get('payment_method')
            payment_proof = request.FILES.get('receipt')

            if not payment_method_id or not payment_proof:
                messages.error(request, 'Пожалуйста, выберите способ оплаты и прикрепите чек')
                return redirect('checkout')

            try:
                payment_method = PaymentMethod.objects.get(id=payment_method_id, user=request.user)

                # Создаем заказ
                order = Order.objects.create(
                    user=request.user,
                    payment_method=payment_method,
                    total_amount=cart.get_total_price(),
                    payment_proof=payment_proof,
                    status='pending'
                )

                # Создаем элементы заказа из корзины
                for item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price
                    )

                # Вместо деактивации просто удаляем корзину
                cart.delete()  # Удаляем корзину после оформления заказа

                messages.success(request, 'Заказ успешно оформлен!')
                return redirect('profile')

            except PaymentMethod.DoesNotExist:
                messages.error(request, 'Выбранный способ оплаты не найден')
                return redirect('checkout')

        context = {
            'cart': cart,
            'payment_methods': payment_methods,
        }
        return render(request, 'checkout.html', context)

    except Cart.DoesNotExist:
        messages.error(request, 'Корзина пуста')
        return redirect('cart_view')



# удаление товара из корзины
@login_required
def remove_from_cart(request, item_id):
    cart_item = CartItem.objects.get(id=item_id)
    if cart_item.cart.user == request.user:
        cart_item.delete()
    return redirect('cart_view')

@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))
        item = CartItem.objects.get(id=item_id)
        item.quantity = quantity
        item.save()
    return redirect('cart_view')


@login_required
def product_list_view(request):
    quaryset = Product.objects.filter(is_active=True)


    if "product_search" in request.GET:
        product_name = request.GET['product_search']
        quaryset = quaryset.filter(title__icontains=product_name)

    products = ProductListFilter(request.GET, queryset=quaryset)

    paginator = Paginator(products.qs, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'main/product_list.html', {'page_obj': page_obj, 'products': products})

