from django.contrib import admin

from .models import Category, Article


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    save_as = True
    save_on_top = True


class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    save_as = True
    save_on_top = True


admin.site.register(Category, CategoryAdmin)
admin.site.register(Article, ArticleAdmin)
