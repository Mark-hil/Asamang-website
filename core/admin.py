from django.contrib import admin
from .models import Appointment, Doctor, GalleryImage

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'department', 'doctor', 'appointment_date', 'status')
    list_filter = ('status', 'department', 'appointment_date')
    search_fields = ('name', 'email', 'phone')
    date_hierarchy = 'appointment_date'
    list_per_page = 20
    ordering = ('-appointment_date', '-appointment_time')
    actions = ['approve_appointments', 'reject_appointments']

    def approve_appointments(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} appointment(s) were successfully approved.')

    def reject_appointments(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} appointment(s) were rejected.')

    approve_appointments.short_description = "Approve selected appointments"
    reject_appointments.short_description = "Reject selected appointments"


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization', 'qualifications', 'is_available')
    list_filter = ('specialization', 'is_available')
    search_fields = ('name', 'specialization', 'qualifications')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'specialization', 'qualifications', 'bio', 'image')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone'),
            'classes': ('collapse',)
        }),
        ('Availability', {
            'fields': ('is_available', 'consultation_fee', 'available_days', 'available_time'),
            'classes': ('collapse',)
        }),
        ('Social Media', {
            'fields': ('twitter', 'facebook', 'instagram', 'linkedin'),
            'classes': ('collapse',)
        }),
    )


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_active', 'order', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('is_active', 'order', 'category')
    ordering = ('order', '-created_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'image', 'description', 'category')
        }),
        ('Advanced Options', {
            'classes': ('collapse',),
            'fields': ('is_active', 'order'),
        }),
    )