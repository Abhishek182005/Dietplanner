from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('diet-plan/', views.diet_plan_form, name='diet_plan_form'),
    path('diet-plan/result/<int:profile_id>/', views.diet_plan_result, name='diet_plan_result'),
    path('recipes/', views.recipes, name='recipes'),
    path('mindful-eating/', views.mindful_eating, name='mindful_eating'),
    path('about/', views.about, name='about'),
]