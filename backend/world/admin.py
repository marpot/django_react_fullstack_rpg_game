from django.contrib import admin
from .models import Adventure, Location, Choice

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1
    fk_name = 'location'

class LocationInline(admin.TabularInline):
    model = Location
    extra = 1

@admin.register(Adventure)
class AdventureAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator')
    inlines = [LocationInline]


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    list_filter = ('order',)
    search_fields = ('title',)
    ordering = ['order']
    inlines = [ChoiceInline]

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'next_location')
    search_fields = ('title',)