from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg
from .models import Product, Rating, RatingAnswer
from .forms import ProductCreateForm, ProductUpdateForm
from django.contrib import messages



def index_view(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'main/index.html', {'products': products})


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

def profile_view(request):
    user = request.user
    products = Product.objects.filter(user=request.user)
    return render(request, 'main/profile.html', {'user': user, 'products': products})