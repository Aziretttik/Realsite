from django.db import models
from django.core.validators import MaxLengthValidator, MinValueValidator
from django.contrib.auth import get_user_model
User = get_user_model()



class Category(models.Model):
    title = models.CharField(
        max_length=123,
        verbose_name='название'
    )
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

class Image(models.Model):
    file = models.FileField(
        upload_to='media/product_file',
        verbose_name='файл'
    )

    def __str__(self):
        return str(self.file)

    class Meta:
        verbose_name = 'изображение продукта'
        verbose_name_plural = 'изображения продуктов'

class Product(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=123,
        verbose_name='название'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        verbose_name='категория'
    )

    description = models.TextField(
        verbose_name='описание'
    )

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='цена'
    )

    main_image = models.ImageField(
        upload_to='media/main_images',
        verbose_name= 'Главная фото'
    )

    images = models.ManyToManyField(
        Image,
        verbose_name='изображения'

    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='активен'
    )

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = 'продукт'
        verbose_name_plural = 'продукты'

class Rating(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name = 'продукт'
    )

    count = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxLengthValidator(5)],
        verbose_name='оценка'
    )

    comment = models.TextField(
        verbose_name='комментарий',
        max_length=200
    )

    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата создания',
    )

    def __str__(self):
        return f'{self.user} ---> {self.product}'

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'

class RatingAnswer(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    rating = models.ForeignKey(
        Rating,
        on_delete=models.CASCADE,
        verbose_name = 'отзыв',
        related_name='rating_answers'
    )
    comment = models.TextField(
         max_length=500,
         verbose_name='комментарий'
    )

    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата создания'
    )

    update_date = models.DateTimeField(
        auto_now=True,
        verbose_name='дата изменения'
    )

    time_limit = models.DateTimeField(
        blank=True,
        null= True,
        verbose_name='ограничение по времени'
    )

    class Meta:
        verbose_name = 'ответ на отзыв'
        verbose_name_plural = 'ответы на отзывы'

    def __str__(self):
        return f'{self.user} ---> {self.rating}'


class PaymentMethod(models.Model):
    DoesNotExist = None
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='payment_methods',
                             verbose_name='пользователь')
    title = models.CharField(max_length=123,
                             verbose_name='название')
    qr_image = models.ImageField(upload_to='media/qr',
                                 verbose_name="QR код")
    created_date = models.DateTimeField(auto_now_add=True,
                                        verbose_name='дата создания')
    class Meta:
        verbose_name = 'способ оплаты'
        verbose_name_plural = 'способы оплаты'

    def __str__(self):
        return f'{self.user} ---> {self.title}'

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('processing', 'В обработке'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_proof = models.ImageField(upload_to='payment_proofs/', null=True, blank=True)
    receipt_number = models.CharField(max_length=50, unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
            return f"Заказ {self.id} от {self.user.email}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.title} - {self.quantity} шт."


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def get_total_price(self):
        return sum(item.get_cost() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'

    def get_cost(self):
        return self.product.price * self.quantity

