# core/views.py

from django.shortcuts import render, redirect
from .models import UserProfile, Ingredient, Recipe
from .forms import UserProfileForm, SearchForm

def home(request):
    return render(request, 'core/home.html')

def diet_plan_form(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            user_profile = form.save()
            # Redirect to results page with the user profile id
            return redirect('diet_plan_result', profile_id=user_profile.id)
    else:
        form = UserProfileForm()
    
    return render(request, 'core/diet_plan_form.html', {'form': form})

def diet_plan_result(request, profile_id):
    user_profile = UserProfile.objects.get(id=profile_id)
    
    # Generate diet plan based on user profile
    diet_plan = generate_diet_plan(user_profile)
    
    return render(request, 'core/diet_plan_result.html', {
        'user_profile': user_profile,
        'diet_plan': diet_plan
    })

def recipes(request):
    # Get all recipes and ingredients
    all_recipes = Recipe.objects.all()
    ingredients = Ingredient.objects.all().order_by('name')  # Order alphabetically
    
    # Initialize a form for search functionality
    form = SearchForm(request.GET or None)
    
    # Initialize search query
    search_query = request.GET.get('search', '')
    
    # Get selected ingredients from GET parameters
    selected_ingredients = request.GET.getlist('ingredients')
    
    # Start with all recipes
    recipes = all_recipes
    
    # Apply text search if provided
    if search_query:
        recipes = recipes.filter(name__icontains=search_query)
    
    # Filter recipes if ingredients are selected
    if selected_ingredients:
        # For each selected ingredient, filter recipes that contain it
        for ingredient_id in selected_ingredients:
            recipes = recipes.filter(ingredients__id=ingredient_id)
        
        # This ensures recipes have ALL selected ingredients, not just any of them
        recipes = recipes.distinct()
    
    # Get detailed information for each ingredient
    ingredients_with_details = []
    for ingredient in ingredients:
        recipe_count = Recipe.objects.filter(ingredients=ingredient).count()
        ingredients_with_details.append({
            'id': ingredient.id,
            'name': ingredient.name,
            'description': ingredient.description,
            'nutritional_value': ingredient.nutritional_value,
            'recipe_count': recipe_count,
        })
    
    return render(request, 'core/recipes.html', {
        'recipes': recipes,
        'ingredients': ingredients_with_details,
        'selected_ingredients': selected_ingredients,
        'form': form
    })
def mindful_eating(request):
    return render(request, 'core/mindful_eating.html')

def about(request):
    return render(request, 'core/about.html')

# Helper function to generate diet plans
def generate_diet_plan(user_profile):
    # Calculate BMR (Basal Metabolic Rate) using the Harris-Benedict equation
    if user_profile.gender == 'M':
        bmr = 88.362 + (13.397 * user_profile.weight) + (4.799 * user_profile.height) - (5.677 * user_profile.age)
    else:
        bmr = 447.593 + (9.247 * user_profile.weight) + (3.098 * user_profile.height) - (4.330 * user_profile.age)
    
    # Apply activity factor
    activity_factors = {
        'low': 1.2,
        'moderate': 1.55,
        'high': 1.725
    }
    daily_calories = bmr * activity_factors[user_profile.activity_level]

    # Calculate macronutrients based on body weight and activity level
    # Protein: 1.6-2.2g per kg for high activity, 1.2-1.6g for moderate, 0.8-1.2g for low
    protein_factors = {'low': 1.0, 'moderate': 1.4, 'high': 2.0}
    protein_per_kg = protein_factors[user_profile.activity_level]
    daily_protein = user_profile.weight * protein_per_kg  # grams

    # Fat: 20-35% of daily calories (using 25% as baseline)
    # 1g fat = 9 calories
    daily_fat = (daily_calories * 0.25) / 9  # grams

    # Carbs: Remaining calories after protein and fat
    # 1g carbs = 4 calories
    protein_calories = daily_protein * 4
    fat_calories = daily_fat * 9
    carb_calories = daily_calories - (protein_calories + fat_calories)
    daily_carbs = carb_calories / 4  # grams

    # Rest of the meal plan logic remains the same
    meal_plan = {
        'breakfast': 'Quick and nutritious breakfast options',
        'lunch': 'Easy-to-pack or campus-friendly lunches',
        'dinner': 'Simple, budget-friendly dinner ideas',
        'snacks': 'Energy-boosting snacks for study sessions'
    }
    if user_profile.activity_level == 'high':
        meal_plan['pre_workout'] = 'Pre-workout nutrition recommendations'
        meal_plan['post_workout'] = 'Post-workout recovery meals'
    
    return {
        'daily_calories': round(daily_calories),
        'meal_plan': meal_plan,
        'macros': {
            'protein': f"{round(daily_protein)} g",
            'carbs': f"{round(daily_carbs)} g",
            'fats': f"{round(daily_fat)} g"
        },
        'macro_ratios': {
            'protein': f"{round((protein_calories/daily_calories)*100)}%",
            'carbs': f"{round((carb_calories/daily_calories)*100)}%",
            'fats': f"{round((fat_calories/daily_calories)*100)}%"
        }
    }