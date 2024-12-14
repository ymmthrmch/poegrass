from .models import Event,Tanka,TankaList
from django.contrib import admin

class EventAdmin(admin.ModelAdmin):
    fields=[
        'start_time',
        'organizer',
        'title',
        'location',
        'deadline',
        'ann_desc'
    ]

class TankaAdmin(admin.ModelAdmin):
    fields=[
        'content',
        'author',
        'status',
    ]

class TankaListAdmin(admin.ModelAdmin):
    fields=[
        'title',
        'owner',
        'is_public',
    ]

admin.site.register(Event,EventAdmin)
admin.site.register(Tanka,TankaAdmin)
admin.site.register(TankaList, TankaListAdmin)
