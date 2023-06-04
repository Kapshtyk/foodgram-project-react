from django.contrib import admin

from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "measurement_unit",
    )
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "-empty-"
    ordering = ("pk",)


admin.site.register(Ingredient, IngredientAdmin)


class TagAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "color", "slug")
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
        "pk",
        "author",
        "name",
        "image",
        "text",
        "cooking_time",
    )
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "-empty-"
    ordering = ("pk",)
    inlines = [RecipeIngredientInline]


admin.site.register(Recipe, RecipeAdmin)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "recipe")
    search_fields = ("user",)
    list_filter = ("user",)
    empty_value_display = "-empty-"
    ordering = ("pk",)


admin.site.register(Favorite, FavoriteAdmin)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "recipe")
    search_fields = ("user",)
    list_filter = ("user",)
    empty_value_display = "-empty-"
    ordering = ("pk",)


admin.site.register(ShoppingCart, ShoppingCartAdmin)
