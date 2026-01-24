from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.validators import MinValueValidator, MaxValueValidator

class Appointment(models.Model):
    APPOINTMENT_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    department = models.CharField(max_length=100)
    doctor = models.CharField(max_length=100)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=APPOINTMENT_STATUS, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.appointment_date} {self.appointment_time}"

    class Meta:
        ordering = ['appointment_date', 'appointment_time']

    def send_status_notification(self, request=None):
        """Send email notification about status change to the patient."""
        from django.conf import settings
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        
        subject = f"Appointment {self.get_status_display()}"
        
        # Get the absolute URL for the appointment
        if request:
            abs_url = request.build_absolute_uri(f'/appointment/{self.id}/')
        else:
            abs_url = f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/appointment/{self.id}/"
        
        context = {
            'appointment': self,
            'status_display': self.get_status_display(),
            'appointment_url': abs_url,
            'site_name': getattr(settings, 'SITE_NAME', 'Our Medical Center'),
            'contact_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
        }
        
        # Render HTML email
        html_message = render_to_string('emails/appointment_status_update.html', context)
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            # Log the error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send appointment status email: {str(e)}")
            return False
