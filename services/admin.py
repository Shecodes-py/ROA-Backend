# from django.contrib import admin
# from .models import *
# from django.utils.html import format_html

# # Register your models here.
# # admin.site.register(FumigationServiceOption)

# @admin.register(Service)
# class ServiceAdmin(admin.ModelAdmin):
#     list_display = ['name', 'service_type', 'base_price', 'is_active']
#     list_filter = ['service_type', 'is_active']
#     search_fields = ['name', 'description']
#     list_editable = ['is_active']


# @admin.register(CleaningServiceOption)
# class CleaningServiceOptionAdmin(admin.ModelAdmin):
#     list_display = ['name', 'cleaning_type', 'service']
#     list_filter = ['cleaning_type', 'service']
#     search_fields = ['name']


# @admin.register(PropertySizeOption)
# class PropertySizeOptionAdmin(admin.ModelAdmin):
#     list_display = ['display_name', 'size_type', 'price_multiplier']
#     list_filter = ['size_type']
#     list_editable = ['price_multiplier']


# @admin.register(AdditionalService)
# class AdditionalServiceAdmin(admin.ModelAdmin):
#     list_display = ['name', 'addon_type', 'price', 'is_active']
#     list_filter = ['addon_type', 'is_active']
#     search_fields = ['name']
#     list_editable = ['price', 'is_active']


# @admin.register(TimeSlot)
# class TimeSlotAdmin(admin.ModelAdmin):
#     list_display = ['display_name', 'start_time', 'end_time', 'is_active']
#     list_filter = ['is_active']
#     list_editable = ['is_active']
#     ordering = ['start_time']


# @admin.register(Schedule)
# class ScheduleAdmin(admin.ModelAdmin):
#     list_display = ['date', 'slot', 'is_available', 'bookings_count']
#     list_filter = ['date', 'is_available', 'slot']
#     search_fields = ['date']
#     list_editable = ['is_available']
#     date_hierarchy = 'date'
    
#     def bookings_count(self, obj):
#         return obj.bookings.count()
#     bookings_count.short_description = 'Bookings'


# @admin.register(ServiceLocation)
# class ServiceLocationAdmin(admin.ModelAdmin):
#     list_display = ['address_line', 'area', 'user']
#     list_filter = ['area']
#     search_fields = ['address_line', 'user__username', 'user__email']


# @admin.register(Booking)
# class BookingAdmin(admin.ModelAdmin):
#     list_display = [
#         'id', 'get_customer_name', 'main_service', 'service_date',
#         'time_slot_display', 'colored_status', 'total_amount', 'booked_at'
#     ]
#     list_filter = [
#         'status', 'service_date', 'main_service__service_type',
#         'is_emergency', 'is_recurring', 'payment_method'
#     ]
#     search_fields = [
#         'first_name', 'last_name', 'email', 'phone',
#         'user__username', 'user__email'
#     ]
#     readonly_fields = [
#         'booked_at', 'updated_at', 'total_amount', 'add_ons_total',
#         'emergency_fee', 'property_multiplier', 'service_date', 'time_slot'
#     ]
#     filter_horizontal = ['additional_services']
#     date_hierarchy = 'service_date'
    
#     fieldsets = (
#         ('Customer Information', {
#             'fields': ('user', 'first_name', 'last_name', 'phone', 'email')
#         }),
#         ('Service Details', {
#             'fields': (
#                 'main_service', 'cleaning_option', 'property_size',
#                 'additional_services', 'is_emergency'
#             )
#         }),
#         ('Schedule & Location', {
#             'fields': ('schedule', 'service_date', 'time_slot', 'location')
#         }),
#         ('Pricing', {
#             'fields': (
#                 'base_price', 'property_multiplier', 'add_ons_total',
#                 'emergency_fee', 'total_amount'
#             )
#         }),
#         ('Payment & Status', {
#             'fields': ('payment_method', 'terms_agreed', 'status')
#         }),
#         ('Recurring', {
#             'fields': ('is_recurring', 'recurring_booking'),
#             'classes': ('collapse',)
#         }),
#         ('Metadata', {
#             'fields': ('booked_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
    
#     def get_customer_name(self, obj):
#         return f"{obj.first_name} {obj.last_name}"
#     get_customer_name.short_description = 'Customer'
    
#     def time_slot_display(self, obj):
#         return obj.time_slot.display_name if obj.time_slot else '-'
#     time_slot_display.short_description = 'Time'
    
#     def colored_status(self, obj):
#         colors = {
#             'pending': '#fbbf24',      # yellow
#             'confirmed': '#10b981',     # green
#             'in_progress': '#3b82f6',   # blue
#             'completed': '#6366f1',     # indigo
#             'cancelled': '#ef4444',     # red
#         }
#         color = colors.get(obj.status, '#6b7280')
#         return format_html(
#             '<span style="color: {}; font-weight: bold;">{}</span>',
#             color,
#             obj.get_status_display()
#         )
#     colored_status.short_description = 'Status'
    
#     actions = ['mark_confirmed', 'mark_completed', 'mark_cancelled']
    
#     def mark_confirmed(self, request, queryset):
#         updated = queryset.update(status='confirmed')
#         self.message_user(request, f'{updated} booking(s) marked as confirmed.')
#     mark_confirmed.short_description = 'Mark as Confirmed'
    
#     def mark_completed(self, request, queryset):
#         updated = queryset.update(status='completed')
#         self.message_user(request, f'{updated} booking(s) marked as completed.')
#     mark_completed.short_description = 'Mark as Completed'
    
#     def mark_cancelled(self, request, queryset):
#         updated = queryset.update(status='cancelled')
#         self.message_user(request, f'{updated} booking(s) marked as cancelled.')
#     mark_cancelled.short_description = 'Mark as Cancelled'


# @admin.register(RecurringBooking)
# class RecurringBookingAdmin(admin.ModelAdmin):
#     list_display = [
#         'id', 'user', 'main_service', 'interval',
#         'start_date', 'end_date', 'is_active'
#     ]
#     list_filter = ['interval', 'is_active', 'start_date']
#     search_fields = ['user__username', 'user__email']
#     filter_horizontal = ['additional_services']
#     readonly_fields = ['created_at', 'updated_at']
    
#     fieldsets = (
#         ('User', {
#             'fields': ('user',)
#         }),
#         ('Service Details', {
#             'fields': (
#                 'main_service', 'cleaning_option', 'property_size',
#                 'additional_services'
#             )
#         }),
#         ('Schedule', {
#             'fields': ('time_slot', 'interval', 'start_date', 'end_date')
#         }),
#         ('Location', {
#             'fields': ('location',)
#         }),
#         ('Status & Metadata', {
#             'fields': ('is_active', 'created_at', 'updated_at')
#         }),
#     )
