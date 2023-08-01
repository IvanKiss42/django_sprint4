from django.contrib import admin

from .models import Category, Post, Location


@admin.register(Category, Post, Location)
class PersonAdmin(admin.ModelAdmin):
    pass


admin.site.empty_value_display = 'Не задано'

"""
Оставил на всякий случай

admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Location)
"""
