# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import *

class UserProfileInline(admin.StackedInline):
    model = UserProfile

class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'teacher') 
    search_fields = ('name', 'code', 'teacher__username') 
    filter_horizontal = ('students',)

@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ('owner', 'question', 'answer', 'subject',)
    search_fields = ('question', 'subject', 'owner__username',)

@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('cost', 'name')
    search_fields = ('name', 'cost')
    ordering = ('cost',)

