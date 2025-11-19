from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import (
    Participant, BergenTikTok, BergenInstagram,
    UCLALoneliness, PrefrontalSymptoms, CAIDS
)
from .serializers import (
    ParticipantSerializer, SurveySubmissionSerializer,
    BergenTikTokSerializer, BergenInstagramSerializer,
    UCLALonelinessSerializer, PrefrontalSymptomsSerializer,
    CAIDSSerializer
)


class SurveyViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    lookup_field = 'email'
    
    @action(detail=False, methods=['post'])
    def submit(self, request):
        """Submit survey responses"""
        serializer = SurveySubmissionSerializer(data=request.data)
        
        if serializer.is_valid():
            participant = serializer.save()
            
            # Send feedback email
            self.send_feedback_email(participant)
            
            return Response({
                'message': 'Encuesta enviada exitosamente',
                'email': participant.email
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def feedback(self, request, email=None):
        """Get feedback for a participant"""
        try:
            participant = Participant.objects.get(email=email)
            feedback = self.generate_feedback(participant)
            return Response(feedback)
        except Participant.DoesNotExist:
            return Response(
                {'error': 'Participante no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def generate_feedback(self, participant):
        """Generate feedback for all completed instruments"""
        feedback = {
            'email': participant.email,
            'instruments': {}
        }
        
        if hasattr(participant, 'bergen_tiktok'):
            feedback['instruments']['bergen_tiktok'] = {
                'score': participant.bergen_tiktok.total_score,
                'feedback': participant.bergen_tiktok.get_feedback()
            }
        
        if hasattr(participant, 'bergen_instagram'):
            feedback['instruments']['bergen_instagram'] = {
                'score': participant.bergen_instagram.total_score,
                'feedback': participant.bergen_instagram.get_feedback()
            }
        
        if hasattr(participant, 'ucla_loneliness'):
            feedback['instruments']['ucla_loneliness'] = {
                'score': participant.ucla_loneliness.total_score,
                'feedback': participant.ucla_loneliness.get_feedback()
            }
        
        if hasattr(participant, 'prefrontal_symptoms'):
            feedback['instruments']['prefrontal_symptoms'] = {
                'score': participant.prefrontal_symptoms.total_score,
                'feedback': participant.prefrontal_symptoms.get_feedback()
            }
        
        if hasattr(participant, 'caids'):
            feedback['instruments']['caids'] = {
                'score': participant.caids.total_score,
                'feedback': participant.caids.get_feedback()
            }
        
        return feedback
    
    def send_feedback_email(self, participant):
        """Send feedback email to participant using Mailgun"""
        from django.core.mail import EmailMultiAlternatives
        from django.template.loader import render_to_string
        
        feedback = self.generate_feedback(participant)
        
        subject = 'Resultados de tu Encuesta Psicológica'
        
        # Create email context
        context = {
            'email': participant.email,
            'location': participant.get_location_display(),
            'instruments': feedback['instruments'],
        }
        
        # Render HTML template
        html_message = self._render_feedback_html(context)
        
        # Create plain text version
        text_message = self._render_feedback_text(context)
        
        # Create email with both plain text and HTML
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[participant.email],
        )
        
        # Attach HTML version
        email.attach_alternative(html_message, "text/html")
        
        try:
            # Send email via Mailgun
            result = email.send()
            
            if result:
                participant.feedback_sent = True
                participant.save()
                print(f"✅ Email sent successfully to {participant.email}")
            else:
                print(f"⚠️ Email sending returned False for {participant.email}")
                
        except Exception as e:
            print(f"❌ Error sending email to {participant.email}: {e}")
            raise

    def _render_feedback_html(self, context):
        """Render HTML email template"""
        from django.template.loader import render_to_string
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f9f9f9;
                }}
                .header {{
                    background: linear-gradient(135deg, #6C63FF 0%, #8B7FFF 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px 10px 0 0;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: bold;
                }}
                .content {{
                    background: white;
                    padding: 30px;
                }}
                .instrument {{
                    margin: 20px 0;
                    padding: 15px;
                    background: #f5f5f5;
                    border-left: 4px solid #6C63FF;
                    border-radius: 5px;
                }}
                .instrument-title {{
                    font-size: 16px;
                    font-weight: bold;
                    color: #6C63FF;
                    margin: 0 0 10px 0;
                }}
                .instrument-score {{
                    font-size: 14px;
                    color: #666;
                    margin: 5px 0;
                }}
                .instrument-feedback {{
                    font-size: 16px;
                    font-weight: bold;
                    color: #333;
                    margin: 10px 0 0 0;
                    padding: 10px;
                    background: white;
                    border-radius: 5px;
                }}
                .feedback-low {{
                    background-color: #d4edda;
                    color: #155724;
                }}
                .feedback-moderate {{
                    background-color: #fff3cd;
                    color: #856404;
                }}
                .feedback-high {{
                    background-color: #f8d7da;
                    color: #721c24;
                }}
                .footer {{
                    background: #f5f5f5;
                    padding: 20px;
                    border-radius: 0 0 10px 10px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                }}
                .disclaimer {{
                    padding: 15px;
                    background: #e7f3ff;
                    border-left: 4px solid #2196F3;
                    margin: 20px 0;
                    font-size: 13px;
                    color: #0c5aa0;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Encuesta Completada</h1>
                    <p>Aquí están tus resultados</p>
                </div>
                
                <div class="content">
                    <p>Hola,</p>
                    <p>Gracias por completar nuestra encuesta psicológica. A continuación encontrarás el resumen de tus resultados:</p>
                    
                    <div style="margin: 30px 0;">
        """
        
        # Add instrument results
        instrument_names = {
            'bergen_tiktok': '📱 Bergen TikTok - Escala de Adicción a TikTok',
            'bergen_instagram': '📸 Bergen Instagram - Escala de Adicción a Instagram',
            'ucla_loneliness': '👥 UCLA - Escala de Soledad',
            'prefrontal_symptoms': '🧠 Síntomas Prefrontales - Inventario Abreviado',
            'caids': '🤖 CAIDS - Dependencia de IA Conversacional',
        }
        
        for instrument, data in context['instruments'].items():
            feedback_class = self._get_feedback_class(data['feedback'])
            html += f"""
                    <div class="instrument">
                        <div class="instrument-title">{instrument_names.get(instrument, instrument)}</div>
                        <div class="instrument-score">Puntuación: {data['score']}</div>
                        <div class="instrument-feedback feedback-{feedback_class}">
                            {data['feedback']}
                        </div>
                    </div>
            """
        
        html += """
                    </div>
                    
                    <div class="disclaimer">
                        <strong>⚠️ Descargo de Responsabilidad:</strong><br>
                        Estos resultados son solo para fines informativos y no constituyen un diagnóstico clínico. 
                        Si tienes preocupaciones sobre tu salud mental o bienestar, te recomendamos consultar con un 
                        profesional de la salud mental calificado.
                    </div>
                    
                    <p>Si tienes preguntas sobre tus resultados o la encuesta, no dudes en contactarnos.</p>
                </div>
                
                <div class="footer">
                    <p>&copy; 2025 Estudio de Evaluación Psicológica. Todos los derechos reservados.</p>
                    <p>Este es un correo automatizado. Por favor no respondas a este mensaje.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    def _render_feedback_text(self, context):
        """Render plain text email"""
        text = "RESULTADOS DE TU ENCUESTA PSICOLÓGICA\n"
        text += "=" * 50 + "\n\n"
        text += f"Correo: {context['email']}\n"
        text += f"Ubicación: {context['location']}\n\n"
        
        instrument_names = {
            'bergen_tiktok': 'Bergen TikTok - Escala de Adicción a TikTok',
            'bergen_instagram': 'Bergen Instagram - Escala de Adicción a Instagram',
            'ucla_loneliness': 'UCLA - Escala de Soledad',
            'prefrontal_symptoms': 'Síntomas Prefrontales - Inventario Abreviado',
            'caids': 'CAIDS - Dependencia de IA Conversacional',
        }
        
        for instrument, data in context['instruments'].items():
            text += f"{instrument_names.get(instrument, instrument)}\n"
            text += "-" * 50 + "\n"
            text += f"Puntuación: {data['score']}\n"
            text += f"Resultado: {data['feedback']}\n\n"
        
        text += "=" * 50 + "\n"
        text += "DESCARGO DE RESPONSABILIDAD:\n"
        text += "Estos resultados son solo para fines informativos y no constituyen\n"
        text += "un diagnóstico clínico. Si tienes preocupaciones sobre tu salud mental,\n"
        text += "te recomendamos consultar con un profesional calificado.\n\n"
        text += "Equipo de Investigación"
        
        return text

    def _get_feedback_class(self, feedback_text):
        """Determine CSS class for feedback styling"""
        if 'bajo' in feedback_text.lower() or 'mínimo' in feedback_text.lower():
            return 'low'
        elif 'moderado' in feedback_text.lower() or 'leve' in feedback_text.lower():
            return 'moderate'
        else:
            return 'high'