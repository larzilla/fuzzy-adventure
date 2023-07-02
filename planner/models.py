from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

class Recipe(models.Model):
    name = models.CharField(max_length=250) # Name of the recipe
    categories = models.ManyToManyField('Category', blank=True, related_name='categories')
    directions = models.TextField() # How to make it
    date_added = models.DateTimeField(auto_now_add=True)
    ingredients = models.TextField(default='None')
    servings = models.IntegerField(blank=True, null=True, default=1)
    prep_time = models.CharField(max_length=250, blank=True, null=True)
    cook_time = models.CharField(max_length=250, blank=True, null=True)
    public = models.BooleanField(default=True)
    author = models.ForeignKey('User', blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"

class Category(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.name}"

class MealPlan(models.Model):
    breakfast1_recipe = models.ForeignKey('Recipe', null=True, blank=True, related_name='breakfast1recipe', on_delete=models.CASCADE)
    breakfast2_recipe = models.ForeignKey('Recipe', null=True, blank=True, related_name='breakfast2recipe', on_delete=models.CASCADE)
    breakfast3_recipe = models.ForeignKey('Recipe', null=True, blank=True, related_name='breakfast3recipe', on_delete=models.CASCADE)
    lunch1_recipe = models.ForeignKey('Recipe', null=True, blank=True, related_name='lunch1recipe', on_delete=models.CASCADE)
    lunch2_recipe = models.ForeignKey('Recipe', null=True, blank=True, related_name='lunch2recipe', on_delete=models.CASCADE)
    dinner1_recipe = models.ForeignKey('Recipe', null=True, blank=True, related_name='dinner1recipe', on_delete=models.CASCADE)
    dinner2_recipe = models.ForeignKey('Recipe', null=True, blank=True, related_name='dinner2recipe', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    saved_by = models.ForeignKey('User', null=True, blank=True, related_name="savedby", on_delete=models.CASCADE)