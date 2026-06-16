from django import forms
from django.forms import ModelForm
from .models import Appointment, Doctor, BlogPost, BlogComment, GalleryImage
from django.forms import ModelForm, Textarea
from django.utils import timezone
from datetime import time, datetime

class AppointmentForm(forms.ModelForm):
    # Define department choices
    DEPARTMENTS = [
        ('', 'Select Department'),
        ('Cardiology', 'Cardiology'),
        ('Neurology', 'Neurology'),
        ('Pediatrics', 'Pediatrics'),
        ('Dermatology', 'Dermatology'),
        ('Orthopedics', 'Orthopedics'),
        ('Gastroenterology', 'Gastroenterology'),
        ('Ophthalmology', 'Ophthalmology'),
    ]
    
    # Add custom validation if needed
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'min': timezone.now().strftime('%Y-%m-%d'),
            'class': 'form-control',
            'required': 'required'
        }),
        validators=[],
        required=True
    )
    
    appointment_time = forms.ChoiceField(
        choices=[
            ('06:00', '06:00 AM'), ('06:30', '06:30 AM'),
            ('07:00', '07:00 AM'), ('07:30', '07:30 AM'),
            ('08:00', '08:00 AM'), ('08:30', '08:30 AM'),
            ('09:00', '09:00 AM'), ('09:30', '09:30 AM'),
            ('10:00', '10:00 AM'), ('10:30', '10:30 AM'),
            ('11:00', '11:00 AM'), ('11:30', '11:30 AM'),
            ('12:00', '12:00 PM'), ('12:30', '12:30 PM'),
            ('13:00', '01:00 PM'), ('13:30', '01:30 PM'),
            ('14:00', '02:00 PM'), ('14:30', '02:30 PM'),
            ('15:00', '03:00 PM'), ('15:30', '03:30 PM'),
            ('16:00', '04:00 PM'), ('16:30', '04:30 PM'),
            ('17:00', '05:00 PM'), ('17:30', '05:30 PM'),
            ('18:00', '06:00 PM')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'appointment_time',
            'required': 'required'
        }),
        required=True
    )
    
    department = forms.ChoiceField(
        choices=DEPARTMENTS,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_department',
            'required': 'required'
        }),
        required=True
    )
    
    doctor = forms.CharField(
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_doctor',
            'required': 'required',
            'disabled': 'disabled'
        }),
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial empty choice for the doctor select
        self.fields['doctor'].widget.choices = [('', 'Select a Doctor')]
    
    class Meta:
        model = Appointment
        fields = ['name', 'email', 'phone', 'department', 'doctor', 'appointment_date', 'appointment_time', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name',
                'required': 'required'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email',
                'required': 'required'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Phone',
                'required': 'required'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Additional Message (Optional)'
            }),
        }
    
    def clean_appointment_date(self):
        appointment_date = self.cleaned_data.get('appointment_date')
        if appointment_date < timezone.now().date():
            raise forms.ValidationError("Appointment date cannot be in the past.")
        return appointment_date
    
    def clean(self):
        cleaned_data = super().clean()
        appointment_date = cleaned_data.get('appointment_date')
        appointment_time_str = cleaned_data.get('appointment_time')
        
        if appointment_date and appointment_time_str:
            try:
                # Parse the time string (format: 'HH:MM')
                time_parts = appointment_time_str.split(':')
                hour = int(time_parts[0])
                minute = int(time_parts[1])
                appointment_time = time(hour, minute)
                
                # Create a timezone-aware datetime for comparison
                appointment_datetime = timezone.make_aware(
                    datetime.combine(appointment_date, appointment_time)
                )
                
                # Check if the appointment is in the past
                if appointment_datetime < timezone.now():
                    raise forms.ValidationError("Appointment date and time cannot be in the past.")
                
                # Check if the appointment is during working hours (9 AM to 5 PM)
                if appointment_time < time(9, 0) or appointment_time > time(17, 0):
                    raise forms.ValidationError("Appointments are only available between 9:00 AM and 5:00 PM.")
                
                # Update the cleaned data with the time object
                cleaned_data['appointment_time'] = appointment_time_str  # Keep the original string for the model
                
            except (ValueError, IndexError) as e:
                raise forms.ValidationError("Invalid time format. Please select a valid time.")
            if appointment_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
                raise forms.ValidationError("Appointments are only available on weekdays (Monday to Friday).")
        
        return cleaned_data


class RejectionForm(forms.Form):
    """Form for providing a reason when rejecting an appointment."""
    reason = forms.CharField(
        label="Reason for Rejection",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Please provide a reason for rejecting this appointment...',
            'required': 'required'
        }),
        help_text="This will be included in the notification email to the patient.",
        required=True
    )


class DoctorForm(forms.ModelForm):
    """Form for creating and updating doctor profiles."""
    class Meta:
        model = Doctor
        fields = '__all__'


class CommentForm(forms.ModelForm):
    """
    Form for submitting comments on blog posts.
    """
    class Meta:
        model = BlogComment
        fields = ['name', 'email', 'body', 'post']
        widgets = {
            'post': forms.HiddenInput(),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name',
                'required': 'required'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email',
                'required': 'required'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Your Comment',
                'required': 'required'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure all fields have the form-control class except hidden fields
        for field_name, field in self.fields.items():
            if field_name != 'post':  # Don't add form-control class to hidden fields
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': f'Your {field_name.capitalize()}',
                })
        # Special handling for the body field
        if 'body' in self.fields:
            self.fields['body'].widget.attrs.update({
                'rows': 4,
            })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        return email.lower().strip() if email else ''


class GalleryImageForm(forms.ModelForm):
    """Form for adding images to the gallery from the frontend."""
    class Meta:
        model = GalleryImage
        fields = ['title', 'image', 'description', 'category']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter image title',
                'required': 'required'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            })
        }
