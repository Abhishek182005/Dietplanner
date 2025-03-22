# core/models.py

from django.db import models

class UserProfile(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    height = models.FloatField(help_text="Height in cm")
    weight = models.FloatField(help_text="Weight in kg")
    
    USER_TYPE_CHOICES = [
        ('working', 'Working Individual'),
        ('student', 'College Student')
    ]
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    
    ACTIVITY_CHOICES = [
        ('low', 'Low Activity'),
        ('moderate', 'Moderate Activity'),
        ('high', 'High Activity - Sports/Gym')
    ]
    activity_level = models.CharField(max_length=10, choices=ACTIVITY_CHOICES)
    
    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    nutritional_value = models.TextField()
    
    def __str__(self):
        return self.name

class Recipe(models.Model):
    name = models.CharField(max_length=100)
    ingredients = models.ManyToManyField(Ingredient)
    instructions = models.TextField()
    preparation_time = models.IntegerField(help_text="Time in minutes")
    image = models.ImageField(
        upload_to='recipes/',
        null=True,
        blank=True,
        help_text="Upload an image of the prepared dish"
    )
    
    def __str__(self):
        return self.name