from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('add/', views.addrecipe, name="addrecipe"),
    path('recipe/<int:recipe_id>', views.viewrecipe, name="viewrecipe"),
    path('recipe/<int:recipe_id>/edit', views.editrecipe, name="editrecipe"),
    path('random', views.random, name="random"),
    path('category/<str:category_name>', views.viewcategory, name="viewcategory"),
    path('categories/', views.viewcategories, name="viewcategories"),
    path('planner/', views.planner, name="planner"),
    path('saveplan/', views.saveplan, name="saveplan"),
    path('mealplan/<int:plan_id>', views.viewplan, name="viewplan"),
    path('viewmyplans/', views.viewmyplans, name="viewmyplans"),
    path('search/', views.search, name="search"),
]