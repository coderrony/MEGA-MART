from django.contrib import admin
from .models import MyUser, UserProfile
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
# Register your models here.


class UserAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name',
                    'username', 'last_login', 'date_added', 'is_active']
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_added')
    ordering = ('date_added',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(MyUser, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="30" style="border-radius:50%;" >'.format(object.profile_image.url))
    thumbnail.short_description = "profile_image"
    list_display = ('thumbnail', 'user', 'city', 'state', 'country')
