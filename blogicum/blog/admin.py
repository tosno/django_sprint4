from django.contrib import admin

from blog.models import Category, Location, Post


admin.site.empty_value_display = 'Не задано'


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'slug',
        'is_published',
        'created_at',
    )
    list_editable = ('is_published',)


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
        'created_at',
    )
    list_editable = ('is_published',)


class PostAdmin(admin.ModelAdmin):
    search_fields = ('text', 'pub_date', 'author',)
    list_display = (
        'id',
        'title',
        'text',
        'is_published',
        'pub_date',
        'author',
        'location',
        'created_at',
    )
    list_display_links = ('title',)
    list_editable = ('text', 'location', 'is_published',)
    list_filter = ('is_published', 'created_at',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
