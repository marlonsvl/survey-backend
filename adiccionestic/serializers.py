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
        fields = ['email', 'location', 'consent_accepted', 'bergen_tiktok', 
                  'bergen_instagram', 'ucla_loneliness', 'prefrontal_symptoms', 'caids']


class SurveySubmissionSerializer(serializers.Serializer):
    email = serializers.EmailField()
    location = serializers.ChoiceField(choices=['EC', 'CL'])
    consent_accepted = serializers.BooleanField()
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
        
        participant, created = Participant.objects.get_or_create(
            email=email,
            defaults={
                'location': location,
                'consent_accepted': consent_accepted,
                'consent_date': timezone.now()
            }
        )
        
        if not created:
            participant.location = location
            participant.consent_accepted = consent_accepted
            participant.consent_date = timezone.now()
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