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
