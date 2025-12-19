from rest_framework import serializers
from .models import Service, CleaningServiceOption, FumigationServiceOption, AdditionalService, LaundryServiceOption

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = 'name', 'description', 'service_type', 'base_price'

    

class CleaningServiceOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CleaningServiceOption
        fields = '__all__'

class FumigationServiceOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FumigationServiceOption
        fields = '__all__'

class LaundryServiceOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaundryServiceOption
        fields = '__all__'

class AdditionalServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalService
        fields = '__all__'
