from django.contrib.auth import get_user_model
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

    images = models.ManyToManyField(
        Image,
        verbose_name='изображения'

    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='активен'
    )

    def __str__(self):
        return str(self.file)

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
        verbose_name='дата создания',
    )

    def __str__(self):
        return self.user

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
        verbose_name = 'отзыв'
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

class Order(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        verbose_name='продукт',
        on_delete=models.CASCADE
    )

    quantity = models.IntegerField(
        verbose_name='количество'
    )

    is_paid = models.BooleanField(
        default=False,
        verbose_name='оплачен'
    )
    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата создания'
    )

