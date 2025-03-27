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
        ('sedentary', 'Sedentary (Little/no exercise)'),
        ('moderate', 'Moderate (3-5 days/week)'),
        ('active', 'Active (6-7 days/week)'),
        ('athlete', 'Athlete (2x/day training)')
    ]
    activity_level = models.CharField(max_length=10, choices=ACTIVITY_CHOICES)

    GOAL_CHOICES = [
        ('lose', 'Weight Loss'),
        ('maintain', 'Maintain Weight'),
        ('gain', 'Gain Weight')
    ]
    goal = models.CharField(max_length=10, choices=GOAL_CHOICES, default='maintain')

    def calculate_bmi(self):
        """Calculate BMI (Body Mass Index)"""
        height_m = self.height / 100  # Convert cm to m
        return round(self.weight / (height_m * height_m), 2)

    def get_bmi_category(self):
        """Get BMI category"""
        bmi = self.calculate_bmi()
        if bmi < 18.5:
            return 'Underweight'
        elif bmi < 25:
            return 'Normal weight'
        elif bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'

    def calculate_bmr(self):
        """Calculate BMR (Basal Metabolic Rate)"""
        if self.gender == 'M':
            return 88.362 + (13.397 * self.weight) + (4.799 * self.height) - (5.677 * self.age)
        else:
            return 447.593 + (9.247 * self.weight) + (3.098 * self.height) - (4.330 * self.age)

    def __str__(self):
        return f"{self.name} - {self.get_goal_display()}"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

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
    
    def __str__(self):
        return self.name