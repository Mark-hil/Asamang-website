from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Home
    path("", views.home, name="home"),
    
    # Main Pages
    path("about/", views.about, name="about"),
    path("departments/", views.departments, name="departments"),
    path("departments/<int:pk>/", views.department_detail, name="department_details"),
    path("services/", views.services, name="services"),
    path("services/<int:pk>/", views.service_detail, name="service_detail"),
    path("doctors/", views.doctors, name="doctors"),
    path("appointment/", views.appointment, name="appointment"),
    path("testimonials/", views.testimonials, name="testimonials"),
    path("faq/", views.faq, name="faq"),
    path("gallery/", views.gallery, name="gallery"),
    path("terms/", views.terms, name="terms"),
    path("privacy/", views.privacy, name="privacy"),
    path("contact/", views.contact, name="contact"),
    path("blog/", views.blog, name="blog"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
]
