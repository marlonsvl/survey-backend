from django.db import models
from django.core.validators import EmailValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone


class Participant(models.Model):
    LOCATION_CHOICES = [
        ('EC', 'Ecuador'),
        ('CL', 'Chile'),
    ]
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    LIVING_WITH_CHOICES = [
        ('alone', 'Solo/a'),
        ('mother', 'Con mamá'),
        ('father', 'Con papá'),
        ('both_parents', 'Con ambos padres'),
        ('parents_siblings', 'Con padres y hermanos'),
        ('parents_siblings_grandparents', 'Con padres, hermanos y abuelos'),
        ('extended_family', 'Con padres, hermanos, abuelos y tíos'),
        ('other', 'Otros'),
    ]
    MARITAL_STATUS_CHOICES = [
        ('single', 'Soltero/a'),
        ('married', 'Casado/a'),
        ('free_union', 'Unión libre'),
        ('divorced', 'Divorciado/a'),
        ('widowed', 'Viudo/a'),
        ('separated', 'Separado/a'),
    ]
    SOCIOECONOMIC_CHOICES = [
        ('high', 'Alto'),
        ('medium', 'Medio'),
        ('low', 'Bajo'),
    ]
    RESIDENCE_SECTOR_CHOICES = [
        ('urban', 'Urbano'),
        ('rural', 'Rural'),
    ]

    EDUCATION_CHOICES = [
        ('none', 'Ninguno'),
        ('primary', 'Primaria'),
        ('secondary', 'Secundaria'),
        ('college', 'Superior'),
        ('postgraduate', 'Postgrado'),
    ]

    SEMESTER = [
        ('1', 'Semestre 1'),
        ('2', 'Semestre 2'),
        ('3', 'Semestre 3'),
        ('4', 'Semestre 4'),
        ('5', 'Semestre 5'),
        ('6', 'Semestre 6'),
        ('7', 'Semestre 7'),
        ('8', 'Semestre 8'),
        ('9', 'Semestre 9'),
        ('10', 'Semestre 10'),
        ('11', 'Semestre 11'),
        ('12', 'Semestre 12'),]


    email = models.EmailField(unique=True, validators=[EmailValidator()])
    location = models.CharField(max_length=2, choices=LOCATION_CHOICES, default='--')
    consent_accepted = models.BooleanField(default=True)
    consent_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    feedback_sent = models.BooleanField(default=False)


    # Sociodemographic information
    country = models.CharField(max_length=100, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(150)])
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    gender_other = models.CharField(max_length=100, null=True, blank=True)
    living_with = models.CharField(max_length=50, choices=LIVING_WITH_CHOICES, null=True, blank=True)
    living_with_other = models.CharField(max_length=200, null=True, blank=True)
    university = models.CharField(max_length=200, null=True, blank=True)
    career = models.CharField(max_length=200, null=True, blank=True)
    current_semester = models.CharField(max_length=50, choices=SEMESTER, null=True, blank=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, null=True, blank=True)
    mother_education_level = models.CharField(max_length=200, choices=EDUCATION_CHOICES, null=True, blank=True)
    father_education_level = models.CharField(max_length=200, choices=EDUCATION_CHOICES, null=True, blank=True)
    mother_age = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(150)])
    father_age = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(150)])
    gpa_last_semester = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    repeated_cycles = models.BooleanField(default=False)
    repeated_cycles_count = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    residence_sector = models.CharField(max_length=20, choices=RESIDENCE_SECTOR_CHOICES, null=True, blank=True)
    socioeconomic_level = models.CharField(max_length=20, choices=SOCIOECONOMIC_CHOICES, null=True, blank=True)
    income_sources = models.CharField(max_length=500, null=True, blank=True)  # Comma-separated or JSON
    
    class Meta:
        db_table = 'participants'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email


class BergenTikTok(models.Model):
    """Bergen TikTok Addiction Scale (6 items, 1-5 Likert scale)"""
    participant = models.OneToOneField(Participant, on_delete=models.CASCADE, related_name='bergen_tiktok')
    
    # Questions based on the Bergen scale structure
    q1_salience = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    q2_tolerance = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    q3_mood_modification = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    q4_relapse = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    q5_withdrawal = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    q6_conflict = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    total_score = models.IntegerField(editable=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bergen_tiktok'
    
    def save(self, *args, **kwargs):
        self.total_score = sum([
            self.q1_salience, self.q2_tolerance, self.q3_mood_modification,
            self.q4_relapse, self.q5_withdrawal, self.q6_conflict
        ])
        super().save(*args, **kwargs)
    
    def get_feedback(self):
        if self.total_score <= 12:
            return "Bajo riesgo de adicción a TikTok"
        elif self.total_score <= 18:
            return "Riesgo moderado de adicción a TikTok"
        else:
            return "Alto riesgo de adicción a TikTok"


class BergenInstagram(models.Model):
    """Bergen Instagram Addiction Scale (6 items, 1-5 Likert scale)"""
    participant = models.OneToOneField(Participant, on_delete=models.CASCADE, related_name='bergen_instagram')
    
    q1_salience = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    q2_tolerance = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    q3_mood_modification = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    q4_relapse = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    q5_withdrawal = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    q6_conflict = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    total_score = models.IntegerField(editable=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bergen_instagram'
    
    def save(self, *args, **kwargs):
        self.total_score = sum([
            self.q1_salience, self.q2_tolerance, self.q3_mood_modification,
            self.q4_relapse, self.q5_withdrawal, self.q6_conflict
        ])
        super().save(*args, **kwargs)
    
    def get_feedback(self):
        if self.total_score <= 12:
            return "Bajo riesgo de adicción a Instagram"
        elif self.total_score <= 18:
            return "Riesgo moderado de adicción a Instagram"
        else:
            return "Alto riesgo de adicción a Instagram"


class UCLALoneliness(models.Model):
    """UCLA Loneliness Scale (20 items, 1-4 Likert scale)"""
    participant = models.OneToOneField(Participant, on_delete=models.CASCADE, related_name='ucla_loneliness')
    
    # 20 items from UCLA Loneliness Scale
    q1 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    q2 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    q3 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    q4 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    q5 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    q6 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    q7 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    q8 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    q9 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    q10 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    q11 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    q12 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    q13 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    q14 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    q15 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    q16 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    q17 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    q18 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    q19 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    q20 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    
    total_score = models.IntegerField(editable=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ucla_loneliness'
    
    def save(self, *args, **kwargs):
        self.total_score = sum([
            getattr(self, f'q{i}') for i in range(1, 21)
        ])
        super().save(*args, **kwargs)
    
    def get_feedback(self):
        if self.total_score <= 35:
            return "Nivel bajo de soledad"
        elif self.total_score <= 50:
            return "Nivel moderado de soledad"
        else:
            return "Nivel alto de soledad"


class PrefrontalSymptoms(models.Model):
    """Abbreviated Prefrontal Symptoms Inventory (20 items, 0-4 Likert scale)"""
    participant = models.OneToOneField(Participant, on_delete=models.CASCADE, related_name='prefrontal_symptoms')
    
    # 20 items from the abbreviated inventory
    q1 = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(4)])
    q2 = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(4)])
    q3 = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(4)])
    q4 = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(4)])
    q5 = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(4)])
    q6 = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(4)])
    q7 = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(4)])
    q8 = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(4)])
    q9 = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(4)])
    q10 = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(4)])
    q11 = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(4)])
    q12 = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(4)])
    q13 = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(4)])
    q14 = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(4)])
    q15 = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(4)])
    q16 = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(4)])
    q17 = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(4)])
    q18 = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(4)])
    q19 = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(4)])
    q20 = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(4)])
    
    total_score = models.IntegerField(editable=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'prefrontal_symptoms'
    
    def save(self, *args, **kwargs):
        self.total_score = sum([
            getattr(self, f'q{i}') for i in range(1, 21)
        ])
        super().save(*args, **kwargs)
    
    def get_feedback(self):
        if self.total_score <= 20:
            return "Síntomas prefrontales mínimos"
        elif self.total_score <= 40:
            return "Síntomas prefrontales leves a moderados"
        else:
            return "Síntomas prefrontales significativos"


class CAIDS(models.Model):
    """Conversational AI Dependency Scale (13 items, 1-5 Likert scale)"""
    participant = models.OneToOneField(Participant, on_delete=models.CASCADE, related_name='caids')
    
    # 13 items from CAIDS
    q1 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    q2 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    q3 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    q4 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    q5 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    q6 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    q7 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    q8 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    q9 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    q10 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    q11 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    q12 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    q13 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    total_score = models.IntegerField(editable=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'caids'
    
    def save(self, *args, **kwargs):
        self.total_score = sum([
            getattr(self, f'q{i}') for i in range(1, 14)
        ])
        super().save(*args, **kwargs)
    
    def get_feedback(self):
        if self.total_score <= 26:
            return "Baja dependencia de IA conversacional"
        elif self.total_score <= 39:
            return "Dependencia moderada de IA conversacional"
        else:
            return "Alta dependencia de IA conversacional"