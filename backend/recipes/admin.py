from django.contrib import admin
from django.db.models import Count

from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "-empty-"
    ordering = ("pk",)


admin.site.register(Ingredient, IngredientAdmin)


class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "slug")
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "-empty-"
    ordering = ("pk",)
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Tag, TagAdmin)


class RecipeIngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
        "total_favorites",
    )
    search_fields = ("name",)
    list_filter = ("name", "author", "tags")
    empty_value_display = "-empty-"
    ordering = ("pk",)
    inlines = [RecipeIngredientInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(total_favorites=Count("favorites"))

    def total_favorites(self, obj):
        return obj.total_favorites

    total_favorites.short_description = "Total Favorites"


admin.site.register(Recipe, RecipeAdmin)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    search_fields = ("user",)
    list_filter = ("user",)
    empty_value_display = "-empty-"
    ordering = ("pk",)


admin.site.register(Favorite, FavoriteAdmin)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    search_fields = ("user",)
    list_filter = ("user",)
    empty_value_display = "-empty-"
    ordering = ("pk",)


admin.site.register(ShoppingCart, ShoppingCartAdmin)
