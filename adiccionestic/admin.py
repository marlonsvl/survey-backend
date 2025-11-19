from django.contrib import admin
from .models import (
    Participant, BergenTikTok, BergenInstagram,
    UCLALoneliness, PrefrontalSymptoms, CAIDS
)


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['email', 'created_at', 'feedback_sent']
    search_fields = ['email']
    list_filter = ['feedback_sent', 'created_at']


@admin.register(BergenTikTok)
class BergenTikTokAdmin(admin.ModelAdmin):
    list_display = ['participant', 'total_score', 'created_at']
    search_fields = ['participant__email']


@admin.register(BergenInstagram)
class BergenInstagramAdmin(admin.ModelAdmin):
    list_display = ['participant', 'total_score', 'created_at']
    search_fields = ['participant__email']


@admin.register(UCLALoneliness)
class UCLALonelinessAdmin(admin.ModelAdmin):
    list_display = ['participant', 'total_score', 'created_at']
    search_fields = ['participant__email']


@admin.register(PrefrontalSymptoms)
class PrefrontalSymptomsAdmin(admin.ModelAdmin):
    list_display = ['participant', 'total_score', 'created_at']
    search_fields = ['participant__email']


@admin.register(CAIDS)
class CAIDSAdmin(admin.ModelAdmin):
    list_display = ['participant', 'total_score', 'created_at']
    search_fields = ['participant__email']
