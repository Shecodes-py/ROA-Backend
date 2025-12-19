from django.contrib import admin
from .models import Service, CleaningServiceOption, FumigationServiceOption, AdditionalService, TimeSlot, Schedule, LaundryServiceOption

# Register your models here.
admin.site.register(Service)
admin.site.register(CleaningServiceOption)
admin.site.register(FumigationServiceOption)
admin.site.register(AdditionalService)
admin.site.register(TimeSlot)
admin.site.register(Schedule)

