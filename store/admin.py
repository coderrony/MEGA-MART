from django.contrib import admin
from .models import Products, Variation, ReviewRating, ProductGallery
import admin_thumbnails
# Register your models here.


@admin_thumbnails.thumbnail('images')
class galleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 0


@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('product_name',)}
    list_display = ['product_name', 'price', 'stock',
                    'category', 'modified_date', 'image', 'is_available']
    ordering = ('created',)
    inlines = [galleryInline]


@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category',
                    'variation_value', 'is_available')
    list_editable = ('variation_category', 'variation_value', 'is_available')


admin.site.register(ReviewRating)
admin.site.register(ProductGallery)
