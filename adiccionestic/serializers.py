from rest_framework import serializers
from django.utils import timezone
from .models import (
    Participant, BergenTikTok, BergenInstagram, 
    UCLALoneliness, PrefrontalSymptoms, CAIDS
)


class BergenTikTokSerializer(serializers.ModelSerializer):
    class Meta:
        model = BergenTikTok
        exclude = ['participant', 'total_score', 'created_at']


class BergenInstagramSerializer(serializers.ModelSerializer):
    class Meta:
        model = BergenInstagram
        exclude = ['participant', 'total_score', 'created_at']


class UCLALonelinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = UCLALoneliness
        exclude = ['participant', 'total_score', 'created_at']


class PrefrontalSymptomsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrefrontalSymptoms
        exclude = ['participant', 'total_score', 'created_at']


class CAIDSSerializer(serializers.ModelSerializer):
    class Meta:
        model = CAIDS
        exclude = ['participant', 'total_score', 'created_at']


class ParticipantSerializer(serializers.ModelSerializer):
    bergen_tiktok = BergenTikTokSerializer(required=False)
    bergen_instagram = BergenInstagramSerializer(required=False)
    ucla_loneliness = UCLALonelinessSerializer(required=False)
    prefrontal_symptoms = PrefrontalSymptomsSerializer(required=False)
    caids = CAIDSSerializer(required=False)
    
    class Meta:
        model = Participant
        fields = [
            'email', 'location', 'consent_accepted',
            # Sociodemographic fields
            'country', 'age', 'gender', 'gender_other',
            'living_with', 'living_with_other',
            'university', 'career', 'current_semester',
            'marital_status',
            'mother_education_level', 'father_education_level',
            'mother_age', 'father_age',
            'gpa_last_semester',
            'repeated_cycles', 'repeated_cycles_count',
            'residence_sector',
            'socioeconomic_level',
            'income_sources',
            # Instruments
            'bergen_tiktok', 'bergen_instagram', 'ucla_loneliness',
            'prefrontal_symptoms', 'caids'
        ]

class SociodemographicDataSerializer(serializers.Serializer):
    """Serializer for sociodemographic information"""
    country = serializers.CharField(max_length=100, required=False, allow_blank=True)
    age = serializers.IntegerField(required=False, min_value=1, max_value=150)
    gender = serializers.ChoiceField(choices=['M', 'F', 'O'], required=False)
    gender_other = serializers.CharField(max_length=100, required=False, allow_blank=True)
    living_with = serializers.ChoiceField(
        choices=['alone', 'mother', 'father', 'both_parents', 'parents_siblings', 
                'parents_siblings_grandparents', 'extended_family', 'other'],
        required=False
    )
    living_with_other = serializers.CharField(max_length=200, required=False, allow_blank=True)
    university = serializers.CharField(max_length=200, required=False, allow_blank=True)
    career = serializers.CharField(max_length=200, required=False, allow_blank=True)
    current_semester = serializers.CharField(max_length=50, required=False, allow_blank=True)
    marital_status = serializers.ChoiceField(
        choices=['single', 'married', 'free_union', 'divorced', 'widowed', 'separated'],
        required=False
    )
    mother_education_level = serializers.CharField(max_length=200, required=False, allow_blank=True)
    father_education_level = serializers.CharField(max_length=200, required=False, allow_blank=True)
    mother_age = serializers.IntegerField(required=False, min_value=1, max_value=150)
    father_age = serializers.IntegerField(required=False, min_value=1, max_value=150)
    gpa_last_semester = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, min_value=0, max_value=100)
    repeated_cycles = serializers.BooleanField(required=False)
    repeated_cycles_count = serializers.IntegerField(required=False, min_value=0)
    residence_sector = serializers.ChoiceField(choices=['urban', 'rural'], required=False)
    socioeconomic_level = serializers.ChoiceField(choices=['high', 'medium', 'low'], required=False)
    income_sources = serializers.CharField(max_length=500, required=False, allow_blank=True)



class SurveySubmissionSerializer(serializers.Serializer):
    email = serializers.EmailField()
    location = serializers.ChoiceField(choices=['EC', 'CL'])
    consent_accepted = serializers.BooleanField()
    
    # Sociodemographic data
    sociodemographic_data = SociodemographicDataSerializer(required=False)
    
    # Survey instruments
    bergen_tiktok = BergenTikTokSerializer(required=False)
    bergen_instagram = BergenInstagramSerializer(required=False)
    ucla_loneliness = UCLALonelinessSerializer(required=False)
    prefrontal_symptoms = PrefrontalSymptomsSerializer(required=False)
    caids = CAIDSSerializer(required=False)
    
    def validate_consent_accepted(self, value):
        if not value:
            raise serializers.ValidationError("Debe aceptar el consentimiento informado")
        return value
    
    def create(self, validated_data):
        email = validated_data.pop('email')
        location = validated_data.pop('location')
        consent_accepted = validated_data.pop('consent_accepted')
        sociodemographic_data = validated_data.pop('sociodemographic_data', {})
        
        # Create or update participant
        participant, created = Participant.objects.get_or_create(
            email=email,
            defaults={
                'location': location,
                'consent_accepted': consent_accepted,
                'consent_date': timezone.now(),
            }
        )
        
        if not created:
            participant.location = location
            participant.consent_accepted = consent_accepted
            participant.consent_date = timezone.now()
        
        # Add sociodemographic data
        if sociodemographic_data:
            for field, value in sociodemographic_data.items():
                setattr(participant, field, value)
        
        participant.save()
        
        # Save each instrument if provided
        for instrument_name in ['bergen_tiktok', 'bergen_instagram', 'ucla_loneliness', 
                                'prefrontal_symptoms', 'caids']:
            if instrument_name in validated_data:
                instrument_data = validated_data[instrument_name]
                model_class = {
                    'bergen_tiktok': BergenTikTok,
                    'bergen_instagram': BergenInstagram,
                    'ucla_loneliness': UCLALoneliness,
                    'prefrontal_symptoms': PrefrontalSymptoms,
                    'caids': CAIDS
                }[instrument_name]
                
                model_class.objects.update_or_create(
                    participant=participant,
                    defaults=instrument_data
                )
        
        return participant