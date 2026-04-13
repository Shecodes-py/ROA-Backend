from rest_framework import serializers
from .models import Booking, AdditionalService

class AdditionalServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalService
        fields = ['id', 'addon_type', 'price', 'name']

class BookingSerializer(serializers.ModelSerializer):
    # We allow the client to send a list of primary keys for add-ons
    additional_services = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=AdditionalService.objects.all(),
        required=False
    )

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['status', 'created_at', 'updated_at', 'total_price']

    def create(self, validated_data):
        # Extract add-ons to handle them after the booking instance is created
        additional_services = validated_data.pop('additional_services', [])
        
        # You can perform server-side price calculation here if you don't 
        # want to trust the front-end's 'total_price'
        booking = Booking.objects.create(**validated_data)
        
        # Set the ManyToMany relationship
        booking.additional_services.set(additional_services)
        
        # Trigger any post-save logic (like sending an email or final price check)
        return booking