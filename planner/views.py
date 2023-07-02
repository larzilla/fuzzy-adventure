from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import render, HttpResponse
from django.db.models import Exists
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django import forms

from random import choice, sample
from markdown2 import Markdown

from .models import Recipe, Category, User, MealPlan

class RecipeForm(forms.Form):
    name = forms.CharField(label="Name")
    servings = forms.CharField(widget=forms.NumberInput(), label="Servings")
    preptime = forms.CharField(label="Prep Time", help_text="Time needed to prepare the ingredients in minutes")
    cooktime = forms.CharField(label="Cook Time", help_text="Time needed for cooking in minutes")
    categories = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple(), queryset=Category.objects.all(), required=False)
    ingredients = forms.CharField(widget=forms.Textarea(), required=False, label="Ingredients", help_text="Enter ingredients separated by commas. For example: 1/2 cup milk, 1 cup flour.")
    directions = forms.CharField(widget=forms.Textarea(), label="Instructions")

    categories.widget.attrs.update({'class': 'category-inputs'})

class RecipeSearchForm(forms.Form):
    terms = forms.CharField(label="Enter a recipe name")

def index(request):
    return render(request, "planner/index.html", {
        "RecipeSearchForm": RecipeSearchForm,
        "recipes": Recipe.objects.all().order_by("name"),
    })

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else: return render(request, "planner/login.html")
    else: 
        return render(request, "planner/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            return render(request, "planner/register.html", {
                "message": "Passwords must match."
            })
        
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "planner/register.html", {
                "message": "Username already in use"
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else: 
        return render(request, "planner/register.html")


def viewrecipe(request, recipe_id):
    markdowner = Markdown()
    recipe = Recipe.objects.get(id=recipe_id)
    directions = markdowner.convert(recipe.directions)
    ingredients = recipe.ingredients.split(',')

    return render(request, "planner/recipe.html", {
        "recipe": recipe,
        "ingredients": ingredients,
        "directions": directions
    })

@csrf_exempt
def editrecipe(request, recipe_id):
    if request.method == "POST":
        form = RecipeForm(request.POST)

        if form.is_valid():
            recipe_to_edit = Recipe.objects.get(pk=recipe_id)
            updated_ingredients = form.cleaned_data['ingredients']
            updated_directions = form.cleaned_data['directions']
            updated_name = form.cleaned_data['name']
            updated_categories = form.cleaned_data['categories']
            updated_servings = form.cleaned_data['servings']
            updated_preptime = form.cleaned_data['preptime']
            updated_cooktime = form.cleaned_data['cooktime']
        
            recipe_to_edit.ingredients = updated_ingredients
            recipe_to_edit.directions = updated_directions
            recipe_to_edit.name = updated_name
            recipe_to_edit.servings = updated_servings
            recipe_to_edit.prep_time = updated_preptime
            recipe_to_edit.cook_time = updated_cooktime
            recipe_to_edit.save()

            # Check for categories to remove
            for category in recipe_to_edit.categories.all():
                cat_obj = Category.objects.get(pk=category.pk)

                if category.pk not in updated_categories.all():
                    recipe_to_edit.categories.remove(cat_obj)
            
            # Check for categories to add
            for category in updated_categories.all():
                cat_obj = Category.objects.get(pk=category.pk)

                if category.pk not in recipe_to_edit.categories.all():
                    recipe_to_edit.categories.add(cat_obj)

            return HttpResponseRedirect(reverse("viewrecipe", kwargs={'recipe_id': recipe_id}))
        else: 
            return render(request, "planner/editRecipe.html", {"recipe_id": recipe_id, "message": "Something went wrong. Could not update the recipe."})
    else: 
        recipe = Recipe.objects.get(pk=recipe_id)
        categories = [category.pk for category in recipe.categories.all()]
        data = {
            'name': recipe.name,
            'categories': categories,
            'ingredients': recipe.ingredients,
            'directions':recipe.directions,
            'servings': recipe.servings,
            'preptime': recipe.prep_time,
            'cooktime': recipe.cook_time,
        }

        return render(request, "planner/editRecipe.html", {
            "recipeForm": RecipeForm(initial=data),
            "recipe_id": recipe_id
        })


def search(request):
    if request.method == "POST":
        form = RecipeSearchForm(request.POST)
        if form.is_valid():
            terms = form.cleaned_data["terms"]
            results = Recipe.objects.filter(name__icontains=terms)
           
            return render(request, "planner/searchResults.html", {
                "results": results
            })


def addrecipe(request):
    if request.method == "POST":
        form = RecipeForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            categories = form.cleaned_data["categories"]
            ingredients = form.cleaned_data["ingredients"]
            directions = form.cleaned_data["directions"]
            servings = form.cleaned_data["servings"]
            preptime = form.cleaned_data["preptime"]
            cooktime = form.cleaned_data["cooktime"]

            print(categories.all())

            if Recipe.objects.filter(name=name).exists():
                return render(request, "planner/addRecipe.html", {
                    "message": "A recipe with the name '%s' already exists"
                })
            else:
                # Create the recipe in the db
                Recipe.objects.create(
                    name = name, 
                    ingredients = ingredients,
                    directions = directions,
                    servings = servings,
                    prep_time = preptime,
                    cook_time = cooktime,
                )
                # Get the id
                new_recipe = Recipe.objects.get(name=name)
                # Add the categories
                for category in categories.all():
                    cat_id = int(category.pk)
                    cat_obj = Category.objects.get(pk=cat_id)
                    new_recipe.categories.add(cat_obj)

                # Go to the recipe page
                return HttpResponseRedirect(reverse('viewrecipe', kwargs={'recipe_id': new_recipe.id}))
        else: 
            print(form.errors, form.data, categories)
            return render(request, "planner/addRecipe.html", {
                "message": "Something went wrong",
                "error": form.errors
            })
    else: 
        return render(request, "planner/addRecipe.html", {
            "recipeForm" : RecipeForm()
        })

def random(request):
    recipes = Recipe.objects.all()
    random_recipe = choice(recipes)
    return HttpResponseRedirect(reverse("viewrecipe", kwargs={'recipe_id': random_recipe.id}))

def viewcategory(request, category_name):
    category = Category.objects.get(name=category_name)
    recipes = Recipe.objects.filter(categories__in=[category]).distinct()
    print(recipes)
    return render(request, "planner/category.html", {
        'category': category, 
        'recipes': recipes 
    })

def viewcategories(request):
    all_categories = Category.objects.all()
    return render(request, "planner/categories.html", {
        'categories': all_categories
    })

@login_required(login_url="/login")
def planner(request):

    breakfastCat = Category.objects.get(name="Breakfast")
    lunchCat = Category.objects.get(name="Lunch")
    dinnerCat = Category.objects.get(name="Dinner")
    ingredients = []

    try:
        breakfastChoices = sample(list(Recipe.objects.filter(categories=breakfastCat)), k=3)
        lunchChoices = sample(list(Recipe.objects.filter(categories=lunchCat)), k=2)
        dinnerChoices = sample(list(Recipe.objects.filter(categories=dinnerCat)), k=2)
    except ValueError:
        return render(request, "planner/mealplan.html", {'message': "Not enough recipes in the database to create a meal plan"})

    ingredients = breakfastChoices[0].ingredients.split(',')
    ingredients += breakfastChoices[1].ingredients.split(',')
    ingredients += breakfastChoices[2].ingredients.split(',')
    ingredients += lunchChoices[0].ingredients.split(',')
    ingredients += lunchChoices[1].ingredients.split(',')
    ingredients += dinnerChoices[0].ingredients.split(',')
    ingredients += dinnerChoices[1].ingredients.split(',')

    # Try to remove any duplicates
    ingredients = list(dict.fromkeys(ingredients))

    return render(request, "planner/mealplan.html", {
        "breakfast1": breakfastChoices[0],
        "breakfast2": breakfastChoices[1],
        "breakfast3": breakfastChoices[2],
        "lunch1": lunchChoices[0],
        "lunch2": lunchChoices[1],
        "dinner1": dinnerChoices[0],
        "dinner2": dinnerChoices[1],
        "ingredients": ingredients,
        "enableSave": True,
        "planname": "for the week"
    })


def saveplan(request):
    # Entries from the form on the planner page will be extracted
    user_id = request.user.id
    breakfast1_id = request.POST["breakfast1_recipe"]
    breakfast2_id = request.POST["breakfast2_recipe"]
    breakfast3_id = request.POST["breakfast3_recipe"]
    lunch1_id = request.POST["lunch1_recipe"]
    lunch2_id = request.POST["lunch2_recipe"]
    dinner1_id = request.POST["dinner1_recipe"]
    dinner2_id = request.POST["dinner2_recipe"]

    breakfast1 = Recipe.objects.get(pk=breakfast1_id)
    breakfast2 = Recipe.objects.get(pk=breakfast2_id)
    breakfast3 = Recipe.objects.get(pk=breakfast3_id)
    lunch1 = Recipe.objects.get(pk=lunch1_id)
    lunch2 = Recipe.objects.get(pk=lunch2_id)
    dinner1 = Recipe.objects.get(pk=dinner1_id)
    dinner2 = Recipe.objects.get(pk=dinner2_id)


    # Use the MealPlan model to save breakfasts, lunches, and dinners, and the user's id
    MealPlan.objects.create(
        breakfast1_recipe = breakfast1,
        breakfast2_recipe = breakfast2,
        breakfast3_recipe = breakfast3,
        lunch1_recipe = lunch1,
        lunch2_recipe = lunch2,
        dinner1_recipe = dinner1,
        dinner2_recipe = dinner2,
        saved_by = User.objects.get(pk=user_id)
    )

    # View saved plans
    return HttpResponseRedirect(reverse("viewmyplans"))

    
def viewplan(request, plan_id):
    mealplan = MealPlan.objects.get(id=plan_id)
    ingredients = []

    ingredients = mealplan.breakfast1_recipe.ingredients.split(',')
    ingredients += mealplan.breakfast2_recipe.ingredients.split(',')
    ingredients += mealplan.breakfast3_recipe.ingredients.split(',')
    ingredients += mealplan.lunch1_recipe.ingredients.split(',')
    ingredients += mealplan.lunch2_recipe.ingredients.split(',')
    ingredients += mealplan.dinner1_recipe.ingredients.split(',')
    ingredients += mealplan.dinner2_recipe.ingredients.split(',')

    return render(request, 'planner/mealplan.html', {
        "breakfast1": mealplan.breakfast1_recipe,
        "breakfast2": mealplan.breakfast2_recipe,
        "breakfast3": mealplan.breakfast3_recipe,
        "lunch1": mealplan.lunch1_recipe,
        "lunch2": mealplan.lunch2_recipe,
        "dinner1": mealplan.dinner1_recipe,
        "dinner2": mealplan.dinner2_recipe,
        "ingredients": ingredients,
        "enableSave": False,
        "planname": f"{mealplan.id} - {mealplan.date.strftime('%m %d, %Y')}"
    })


@login_required(login_url="/login")
def viewmyplans(request):
    # Get id of the logged in user
    user_id = request.user.id
    mealplans = MealPlan.objects.filter(saved_by=user_id).order_by('date')

    return render(request, 'planner/mymealplans.html', {'mealplans':mealplans})