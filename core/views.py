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
    return render(request, "department_detail.html", {
        # 'department': department
    })

# Services
def services(request):
    return render(request, "services.html")

def service_detail(request, pk):
    # service = get_object_or_404(Service, pk=pk)
    return render(request, "service_detail.html", {
        # 'service': service
    })

# Doctors
def doctors(request):
    return render(request, "doctors.html")

# Appointment
def appointment(request):
    return render(request, "appointment.html")

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
