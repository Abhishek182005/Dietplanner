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
    # --- Input Validation ---
    required_fields = ['weight', 'height', 'age', 'gender', 'activity_level']
    for field in required_fields:
        if not hasattr(user_profile, field):
            raise ValueError(f"Missing field: {field}")
    
    if user_profile.weight <= 0 or user_profile.height <= 0 or user_profile.age <= 0:
        raise ValueError("Weight, height, and age must be positive.")
    
    if user_profile.gender not in ['M', 'F']:
        raise ValueError("Gender must be 'M' or 'F'.")
    
    # Normalize activity levels to match both implementations
    activity_mapping = {
        'low': 'sedentary',
        'moderate': 'moderate', 
        'high': 'active',
        'sedentary': 'sedentary',
        'active': 'active',
        'athlete': 'athlete'
    }
    mapped_activity = activity_mapping.get(user_profile.activity_level, 'moderate')

    # --- BMR Calculation (Combining both methods) ---
    # Mifflin-St Jeor Equation with option for Harris-Benedict fallback
    if user_profile.gender == 'M':
        bmr_mifflin = 10 * user_profile.weight + 6.25 * user_profile.height - 5 * user_profile.age + 5
        bmr_harris = 88.362 + (13.397 * user_profile.weight) + (4.799 * user_profile.height) - (5.677 * user_profile.age)
    else:
        bmr_mifflin = 10 * user_profile.weight + 6.25 * user_profile.height - 5 * user_profile.age - 161
        bmr_harris = 447.593 + (9.247 * user_profile.weight) + (3.098 * user_profile.height) - (4.330 * user_profile.age)
    
    # Use average of both methods for more robust calculation
    bmr = (bmr_mifflin + bmr_harris) / 2

    # --- Activity Multipliers ---
    activity_factors = {
        'sedentary': 1.2,      # Little/no exercise
        'moderate': 1.55,      # 3-5 days/week
        'active': 1.725,       # 6-7 days/week
        'athlete': 1.9         # 2x/day training
    }
    daily_calories = bmr * activity_factors[mapped_activity]

    # --- Goal Handling (Optional) ---
    goal = getattr(user_profile, 'goal', 'maintain')
    if goal == 'lose':
        daily_calories -= 500  # Safe deficit (~0.5kg/week)
    elif goal == 'gain':
        daily_calories += 500  # Lean bulk (~0.5kg/week)
    daily_calories = max(daily_calories, bmr * 1.1)  # Prevent extreme undereating

    # --- Protein Calculation ---
    protein_ranges = {
        'sedentary': 1.2,      # g/kg body weight
        'moderate': 1.6,
        'active': 2.0,
        'athlete': 2.5
    }
    protein_per_kg = protein_ranges[mapped_activity]
    daily_protein = round(user_profile.weight * protein_per_kg)
    protein_calories = daily_protein * 4

    # --- Fat Calculation ---
    fat_percent = 0.25  # Baseline (20-35% range)
    fat_min = user_profile.weight * 0.5
    daily_fat = max(fat_min, round((daily_calories * fat_percent) / 9))
    fat_calories = daily_fat * 9

    # --- Carb Calculation ---
    remaining_cals = max(0, daily_calories - (protein_calories + fat_calories))
    daily_carbs = round(remaining_cals / 4)

    # --- Macro Ratios ---
    total_calories = protein_calories + (daily_carbs * 4) + fat_calories
    protein_ratio = protein_calories / total_calories
    carb_ratio = (daily_carbs * 4) / total_calories
    fat_ratio = fat_calories / total_calories

    # --- Meal Plan ---
    meal_plan = {
        'breakfast': f"{daily_protein//4}g protein, {daily_carbs//4}g carbs, {daily_fat//4}g fat",
        'lunch': f"{daily_protein//4}g protein, {daily_carbs//4}g carbs, {daily_fat//4}g fat",
        'dinner': f"{daily_protein//4}g protein, {daily_carbs//4}g carbs, {daily_fat//4}g fat",
        'snacks': f"{daily_protein//4}g protein, {daily_carbs//4}g carbs, {daily_fat//4}g fat"
    }

    # Add workout meals for more active individuals
    if mapped_activity in ['active', 'athlete', 'high']:
        meal_plan['pre_workout'] = f"{daily_protein//5}g protein, {daily_carbs//2}g carbs"
        meal_plan['post_workout'] = f"{daily_protein//3}g protein, {daily_carbs//3}g carbs"

    return {
        'daily_calories': round(daily_calories),
        'macros': {
            'protein': f"{daily_protein} g",
            'carbs': f"{daily_carbs} g",
            'fats': f"{daily_fat} g"
        },
        'macro_ratios': {
            'protein': f"{round(protein_ratio * 100)}%",
            'carbs': f"{round(carb_ratio * 100)}%",
            'fats': f"{round(fat_ratio * 100)}%"
        },
        'meal_plan': meal_plan
    }