from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.validators import MinValueValidator, MaxValueValidator

class Doctor(models.Model):
    """Model representing a doctor in the system."""
    SPECIALIZATION_CHOICES = [
        ('Cardiology', 'Cardiology'),
        ('Neurology', 'Neurology'),
        ('Pediatrics', 'Pediatrics'),
        ('Dermatology', 'Dermatology'),
        ('Orthopedics', 'Orthopedics'),
        ('Gastroenterology', 'Gastroenterology'),
        ('Ophthalmology', 'Ophthalmology'),
        ('Oncology', 'Oncology'),
        ('General', 'General Medicine'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES)
    qualifications = models.CharField(max_length=200, help_text="e.g., MBBS, MD, etc.")
    experience = models.PositiveIntegerField(help_text="Years of experience")
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='doctors/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Social Media (optional)
    twitter = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    
    # Schedule
    available_days = models.CharField(max_length=100, default='Monday-Friday', 
                                    help_text="e.g., Monday-Friday, Weekends")
    available_time = models.CharField(max_length=100, default='9:00 AM - 5:00 PM')
    
    def __str__(self):
        return f"Dr. {self.name} - {self.specialization}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.specialization}")
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('doctors:doctor_detail', kwargs={'slug': self.slug})
    
    class Meta:
        ordering = ['name']


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


class BlogPost(models.Model):
    """Model representing a blog post."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.CharField(max_length=100, default='General')
    content = models.TextField()
    excerpt = models.TextField(max_length=300, blank=True)
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    published_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.CharField(max_length=200, blank=True, help_text='Comma-separated tags')
    view_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-published_date']
        
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.title)
            unique_slug = slug
            num = 1
            while BlogPost.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{slug}-{num}"
                num += 1
            self.slug = unique_slug
            
        if not self.excerpt and self.content:
            self.excerpt = self.content[:200] + '...'
            
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('core:blog_detail', kwargs={'slug': self.slug})
    
    def get_tags(self):
        """Return a list of tags."""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',')]
    
    def increment_view_count(self):
        """Increment the view count for this post."""
        self.view_count += 1
        self.save(update_fields=['view_count'])


class BlogComment(models.Model):
    """Model representing comments on blog posts."""
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f'Comment by {self.name} on {self.post}'



# core/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _

class GalleryImage(models.Model):
    class Category(models.TextChoices):
        NATURE = 'nature', _('Nature')
        ARCHITECTURE = 'architecture', _('Architecture')
        PEOPLE = 'people', _('People')
        EVENTS = 'events', _('Events')
    
    title = models.CharField(max_length=200, help_text="A descriptive title for the image")
    image = models.ImageField(upload_to='gallery/%Y/%m/')
    description = models.TextField(blank=True, help_text="Optional image description")
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.EVENTS,
        help_text="Category for filtering"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Order in which the image appears in the gallery")

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = _('Gallery Image')
        verbose_name_plural = _('Gallery Images')

    def __str__(self):
        return self.title