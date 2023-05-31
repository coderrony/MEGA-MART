from django.db import models
from django.urls import reverse
# Create your models here.


class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=250, blank=True)
    category_img = models.ImageField(
        upload_to="category/", blank=True, null=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'categories'

    def __str__(self) -> str:
        return self.category_name

    def get_url(self):
        return reverse('product_item', args=[self.slug])
