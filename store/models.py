from django.db import models
from category.models import Category
from django.urls import reverse
from accounts.models import MyUser
from django.db.models import Sum, Avg, Count, Max, Min
# Create your models here.


class Products(models.Model):
    product_name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField(max_length=400)
    price = models.IntegerField()
    image = models.ImageField(upload_to='product/')
    stock = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    modified_date = models.DateField(auto_now=True)
    created = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.product_name

    def get_url(self):
        return reverse('single_item', args=[self.category.slug, self.slug])

    def averageRating(self):
        average_rating = ReviewRating.objects.filter(
            product_id=self.id, status=True).aggregate(average=Avg('rating'))

        avg_count = 0
        if average_rating['average']:
            avg_count = average_rating['average']

        return avg_count

    class Meta:
        ordering = ['created']
        verbose_name = 'Productss'
        verbose_name_plural = 'Products'


choice_category = (
    ('size', 'size'),
    ('color', 'color'),
)


class Variation(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    variation_category = models.CharField(
        max_length=100, choices=choice_category)
    variation_value = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.variation_value


class ReviewRating(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.subject


class ProductGallery(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    images = models.ImageField(
        upload_to="galleryImage/", default="./default_img.png")

    def __str__(self) -> str:
        return self.product.product_name

    class Meta:
        verbose_name = 'ProductGallerys'
        verbose_name_plural = 'product gallery'
