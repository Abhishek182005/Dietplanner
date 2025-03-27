from django.contrib import admin


admin.site.site_header = 'Fuel My Semester Admin'
admin.site.site_title = 'Fuel My Semester Admin'
admin.site.index_title = 'Welcome to Fuel My Semester Admin'
# Register your models here.
from core.models import UserProfile, Ingredient, Recipe

admin.site.register(UserProfile)
admin.site.register(Ingredient)
admin.site.register(Recipe)

# Register your models here.
