from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q

from .models import Doctor
from .forms import DoctorForm

class DoctorListView(ListView):
    model = Doctor
    template_name = 'doctors.html'
    context_object_name = 'doctors'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Doctor.objects.all().order_by('name')
        
        # Filter by search query
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(specialization__icontains=search_query) |
                Q(qualifications__icontains=search_query)
            )
        
        # Filter by specialization
        specialization = self.request.GET.get('specialization')
        if specialization:
            queryset = queryset.filter(specialization=specialization)
        
        # Only filter by availability if explicitly requested
        available = self.request.GET.get('available')
        if available == 'true':
            queryset = queryset.filter(is_available=True)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['specializations'] = Doctor.SPECIALIZATION_CHOICES
        
        # Preserve filter parameters in pagination
        if self.request.GET.get('search'):
            context['search_query'] = self.request.GET.get('search')
        if self.request.GET.get('specialization'):
            context['specialization'] = self.request.GET.get('specialization')
        if self.request.GET.get('available'):
            context['available'] = self.request.GET.get('available')
            
        return context


class DoctorDetailView(DetailView):
    model = Doctor
    template_name = 'doctors/doctor_detail.html'
    context_object_name = 'doctor'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


class DoctorCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Doctor
    form_class = DoctorForm
    template_name = 'doctors/doctor_form.html'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        messages.success(self.request, 'Doctor profile created successfully!')
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse_lazy('core:doctors')


class DoctorUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Doctor
    form_class = DoctorForm
    template_name = 'doctors/doctor_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        messages.success(self.request, 'Doctor profile updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('core:doctors')


class DoctorDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Doctor
    template_name = 'doctors/doctor_confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('core:doctors')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Doctor profile deleted successfully!')
        return super().delete(request, *args, **kwargs)