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
        queryset=AdditionalService.objects.filter(is_active=True),
        required=False
    )
    customer_name = serializers.CharField(read_only=True)
    additional_services_detail = AdditionalServiceSerializer(
        source='additional_services', many=True, read_only=True
        )
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = [
            'status', 'created_at', 'updated_at',
            'base_price', 'addons_total', 'total_price',
            'customer_name',
        ]

    def create(self, validated_data):
        additional_services = validated_data.pop('additional_services', [])

        # Attach authenticated user if not explicitly supplied
        request = self.context.get('request')
        if request and request.user.is_authenticated and not validated_data.get('user'):
            validated_data['user'] = request.user

        booking = Booking.objects.create(**validated_data)
        booking.additional_services.set(additional_services)

        # Calculate price server-side now that M2M is set
        booking.calculate_price()
        booking.save(update_fields=['base_price', 'addons_total', 'total_price'])

        return booking

    def update(self, instance, validated_data):
        additional_services = validated_data.pop('additional_services', None)
        instance = super().update(instance, validated_data)

        if additional_services is not None:
            instance.additional_services.set(additional_services)

        instance.calculate_price()
        instance.save(update_fields=['base_price', 'addons_total', 'total_price'])
        return instance


class BookingListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    customer_name = serializers.CharField(read_only=True)
    payment_status = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'customer_name', 'main_service', 'property_size',
            'service_date', 'location', 'total_price',
            'status', 'payment_status', 'created_at',
        ]

    def get_payment_status(self, obj):
        # Pull latest payment status for this booking
        payment = obj.payments.order_by('-created_at').first()
        if not payment:
            return 'unpaid'
        return payment.status