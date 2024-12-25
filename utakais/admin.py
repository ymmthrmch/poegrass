from .models import Event,Participant,Tanka,TankaList
from django.contrib import admin

class EventAdmin(admin.ModelAdmin):
    fields=[
        'start_time',
        'organizer',
        'title',
        'location',
        'deadline',
        'ann_desc',
        'ann_status',
    ]

class TankaAdmin(admin.ModelAdmin):
    fields=[
        'content',
        'author',
        'guest_author',
        'status',
    ]

class TankaListAdmin(admin.ModelAdmin):
    fields=[
        'title',
        'owner',
        'is_public',
    ]

class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 1

admin.site.register(Event,EventAdmin)
admin.site.register(Tanka,TankaAdmin)
admin.site.register(TankaList, TankaListAdmin)
admin.site.register(Participant)
