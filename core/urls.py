from django.urls import path
from . import views
from .doctor_views import (
    DoctorListView, DoctorDetailView, 
    DoctorCreateView, DoctorUpdateView, 
    DoctorDeleteView
)
from .blog_views import (
    BlogPostListView, BlogPostDetailView, 
    BlogPostCreateView, BlogPostUpdateView, 
    BlogPostDeleteView, add_comment_to_post,
    CommentUpdateView, CommentDeleteView
)
from .views import GalleryView

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
    
    # Doctors URLs
    path("doctors/", DoctorListView.as_view(), name="doctors"),
    path("doctors/add/", DoctorCreateView.as_view(), name="doctor_create"),
    path("doctors/<slug:slug>/", DoctorDetailView.as_view(), name="doctor_detail"),
    path("doctors/<slug:slug>/edit/", DoctorUpdateView.as_view(), name="doctor_update"),
    path("doctors/<slug:slug>/delete/", DoctorDeleteView.as_view(), name="doctor_delete"),
    
    # Other URLs
    path("appointment/", views.appointment, name="appointment"),
    path("testimonials/", views.testimonials, name="testimonials"),
    path("faq/", views.faq, name="faq"),
    path("gallery/", GalleryView.as_view(), name="gallery"),
    path("terms/", views.terms, name="terms"),
    path("privacy/", views.privacy, name="privacy"),
    path("contact/", views.contact, name="contact"),
    # Blog URLs
    path("blog/", BlogPostListView.as_view(), name="blog"),
    path("blog/create/", BlogPostCreateView.as_view(), name="blog_create"),
    path("blog/<slug:slug>/", BlogPostDetailView.as_view(), name="blog_detail"),
    path("blog/<slug:slug>/edit/", BlogPostUpdateView.as_view(), name="blog_update"),
    path("blog/<slug:slug>/delete/", BlogPostDeleteView.as_view(), name="blog_delete"),
    path("blog/<slug:slug>/comment/", add_comment_to_post, name="add_comment"),
    path("comments/<int:pk>/edit/", CommentUpdateView.as_view(), name="edit_comment"),
    path("comments/<int:pk>/delete/", CommentDeleteView.as_view(), name="delete_comment"),

    # Gallery URLs
    # path("gallery/add/", views.gallery_add, name="gallery_add"),
    # path("gallery/<int:pk>/edit/", views.gallery_edit, name="gallery_edit"),
    # path("gallery/<int:pk>/delete/", views.gallery_delete, name="gallery_delete"),

    # Admin Dashboard and Staff Management
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("staff/signup/", views.staff_signup, name="staff_signup"),
    path("appointments/approve/<int:pk>/", views.approve_appointment, name="approve_appointment"),
    path("appointments/reject/<int:pk>/", views.reject_appointment, name="reject_appointment"),
]
