from django.contrib import admin
from .models import Appointment

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