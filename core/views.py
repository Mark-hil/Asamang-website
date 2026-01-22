from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView

# Home
def home(request):
    return render(request, "home.html")

# About
def about(request):
    return render(request, "about.html")

# Departments
def departments(request):
    return render(request, "departments.html")

def department_detail(request, pk):
    # department = get_object_or_404(Department, pk=pk)
    return render(request, "department_details.html", {
        # 'department': department
    })

# Services
def services(request):
    return render(request, "services.html")

def service_detail(request, pk):
    # service = get_object_or_404(Service, pk=pk)
    return render(request, "service_details.html", {
        # 'service': service
    })

# Doctors
def doctors(request):
    return render(request, "doctors.html")

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from django.contrib.auth import get_user_model
from .forms import AppointmentForm
from .auth_forms import StaffSignupForm
from .models import Appointment

User = get_user_model()

# Appointment
@require_http_methods(["GET", "POST"])
def appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.save()
            messages.success(request, 'Your appointment has been booked successfully! We will contact you shortly to confirm.')
            return redirect('core:appointment')
        else:
            # If the form is invalid, we'll let the template handle the errors
            pass
    else:
        # Pre-fill form with any GET parameters (useful for pre-selecting doctor/department)
        initial_data = {}
        if 'doctor' in request.GET:
            initial_data['doctor'] = request.GET.get('doctor')
        if 'department' in request.GET:
            initial_data['department'] = request.GET.get('department')
        form = AppointmentForm(initial=initial_data)
    
    # Sample data for the form - in a real app, you'd get this from your database
    departments = [
        'Cardiology', 'Neurology', 'Pediatrics', 'Dermatology', 
        'Orthopedics', 'Gastroenterology', 'Ophthalmology'
    ]
    
    doctors = {
        'Cardiology': ['Dr. John Smith', 'Dr. Sarah Johnson'],
        'Neurology': ['Dr. Michael Brown', 'Dr. Emily Davis'],
        'Pediatrics': ['Dr. Robert Wilson', 'Dr. Jennifer Lee'],
        'Dermatology': ['Dr. David Miller'],
        'Orthopedics': ['Dr. James Wilson', 'Dr. Lisa Taylor'],
        'Gastroenterology': ['Dr. Richard Anderson'],
        'Ophthalmology': ['Dr. Patricia Moore']
    }
    
    # Get the selected department from the form data or initial data
    selected_department = None
    if request.method == 'POST':
        selected_department = request.POST.get('department')
    elif 'department' in request.GET:
        selected_department = request.GET.get('department')
    
    # Filter doctors based on selected department
    available_doctors = doctors.get(selected_department, []) if selected_department else []
    
    return render(request, 'appointment.html', {
        'form': form,
        'departments': departments,
        'available_doctors': available_doctors,
    })

# Other Pages
def testimonials(request):
    return render(request, "testimonials.html")

def faq(request):
    return render(request, "faq.html")

def gallery(request):
    return render(request, "gallery.html")

def terms(request):
    return render(request, "terms.html")

def privacy(request):
    return render(request, "privacy.html")

def contact(request):
    return render(request, "contact.html")

def blog(request):
    """
    View function for the blog page that lists all blog posts.
    """
    # In a real application, you would fetch blog posts from the database here
    # For now, we'll just render the template
    return render(request, "blog.html")

def blog_detail(request, slug):
    """
    View function for individual blog post pages.
    
    Args:
        slug (str): The URL-friendly identifier for the blog post
    """
    # In a real application, you would fetch the blog post with the given slug from the database
    # For now, we'll just render the template with some sample data
    post = {
        'title': '10 Tips for a Healthier Lifestyle',
        'slug': slug,
        'content': 'This is a sample blog post content...',
        'published_date': 'January 22, 2025',
        'author': 'Dr. Sarah Johnson',
        'categories': ['Health Tips', 'Lifestyle'],
        'tags': ['health', 'wellness', 'lifestyle'],
    }
    
    return render(request, "blog_detail.html", {
        'post': post
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    """Admin dashboard view that shows all appointments with filtering."""
    # Get counts for the stats cards
    counts = Appointment.objects.aggregate(
        pending=Count('id', filter=Q(status='pending')),
        confirmed=Count('id', filter=Q(status='confirmed')),
        cancelled=Count('id', filter=Q(status='cancelled'))
    )
    
    # Get appointments for each tab
    pending_appointments = Appointment.objects.filter(status='pending').order_by('appointment_date', 'appointment_time')
    confirmed_appointments = Appointment.objects.filter(status='confirmed').order_by('-appointment_date', 'appointment_time')
    cancelled_appointments = Appointment.objects.filter(status='cancelled').order_by('-updated_at')
    
    return render(request, 'admin/dashboard.html', {
        'pending_appointments': pending_appointments,
        'confirmed_appointments': confirmed_appointments,
        'cancelled_appointments': cancelled_appointments,
        'pending_count': counts['pending'],
        'confirmed_count': counts['confirmed'],
        'cancelled_count': counts['cancelled'],
        'title': 'Admin Dashboard',
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
def staff_signup(request):
    """View for staff users to register new staff members."""
    if request.method == 'POST':
        form = StaffSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Successfully created staff account for {user.get_full_name() or user.username}.')
            return redirect('core:admin_dashboard')
    else:
        form = StaffSignupForm()
    
    return render(request, 'admin/staff_signup.html', {
        'form': form,
        'title': 'Add New Staff Member',
    })
@login_required
@user_passes_test(lambda u: u.is_staff)
def approve_appointment(request, pk):
    """View to approve a pending appointment."""
    appointment = get_object_or_404(Appointment, pk=pk)
    if appointment.status == 'pending':
        appointment.status = 'confirmed'
        appointment.save()
        messages.success(request, f"Appointment for {appointment.name} has been approved.")
        # Here you can add email notification logic
    return redirect('core:admin_dashboard')
@login_required
@user_passes_test(lambda u: u.is_staff)
def reject_appointment(request, pk):
    """View to reject a pending appointment."""
    appointment = get_object_or_404(Appointment, pk=pk)
    if appointment.status == 'pending':
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, f"Appointment for {appointment.name} has been rejected.")
        # Here you can add email notification logic
    return redirect('core:admin_dashboard')