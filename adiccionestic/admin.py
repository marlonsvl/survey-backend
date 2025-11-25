from django.contrib import admin
from .models import (
    Participant, BergenTikTok, BergenInstagram,
    UCLALoneliness, PrefrontalSymptoms, CAIDS
)


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['email', 'location', 'age', 'gender', 'university', 'consent_accepted', 'created_at', 'feedback_sent']
    search_fields = ['email', 'country', 'university']
    list_filter = ['location', 'gender', 'marital_status', 'residence_sector', 'socioeconomic_level', 'consent_accepted', 'feedback_sent', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'consent_date']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('email', 'location', 'country')
        }),
        ('Consent', {
            'fields': ('consent_accepted', 'consent_date')
        }),
        ('Personal Information', {
            'fields': ('age', 'gender', 'gender_other', 'marital_status')
        }),
        ('Living Situation', {
            'fields': ('living_with', 'living_with_other')
        }),
        ('Academic Information', {
            'fields': ('university', 'career', 'current_semester', 'gpa_last_semester', 'repeated_cycles', 'repeated_cycles_count')
        }),
        ('Family Information', {
            'fields': ('mother_education_level', 'father_education_level', 'mother_age', 'father_age')
        }),
        ('Socioeconomic Information', {
            'fields': ('residence_sector', 'socioeconomic_level', 'income_sources')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at', 'feedback_sent'),
            'classes': ('collapse',)
        }),
    )


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
