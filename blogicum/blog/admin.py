from django.contrib import admin

from blog.models import Category, Location, Post


admin.site.empty_value_display = 'Не задано'


class PostInLine(admin.StackedInline):
    model = Post
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    inlines = (PostInLine,)
    list_display = (
        'title',
        'slug',
        'is_published',
    )


class LocationAdmin(admin.ModelAdmin):
    inlines = (PostInLine,)
    list_display = (
        'name',
        'is_published',
    )


class PostAdmin(admin.ModelAdmin):
    search_fields = ('category', 'location', 'is_published',)
    list_display = (
        'title',
        'pub_date',
        'author',
        'location',
        'is_published',
        'created_at',
    )
    list_display_links = ('title',)
    list_editable = ('is_published',)
    list_filter = ('category', 'location', 'is_published',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
