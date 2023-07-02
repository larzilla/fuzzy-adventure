from django.contrib import admin
from .models import Recipe, Category, User, MealPlan

admin.site.register(User)
admin.site.register(Recipe)
admin.site.register(Category)
admin.site.register(MealPlan)
