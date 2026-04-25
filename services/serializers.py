from rest_framework import serializers
from .models import Booking, AdditionalService
from .models import PropertySizeChoice


class AdditionalServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalService
        fields = ['id', 'addon_type', 'price', 'name']


class BookingSerializer(serializers.ModelSerializer):
    additional_services = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=AdditionalService.objects.filter(is_active=True),
        required=False
    )
    customer_name = serializers.CharField(read_only=True)
    additional_services_detail = AdditionalServiceSerializer(
        source='additional_services', many=True, read_only=True
    )

    property_size = serializers.ChoiceField(
    choices=PropertySizeChoice.choices, 
    allow_null=True, 
    allow_blank=True, 
    required=False
)

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = [
            'status', 'created_at', 'updated_at',
            'base_price', 'addons_total', 'total_price',
            'emergency_charge', 'customer_name',
        ]

    def create(self, validated_data):
        additional_services = validated_data.pop('additional_services', [])

        request = self.context.get('request')
        if request and request.user.is_authenticated and not validated_data.get('user'):
            validated_data['user'] = request.user

        booking = Booking.objects.create(**validated_data)
        booking.additional_services.set(additional_services)
        # signal handles recalculation after M2M is set, no need to call save() again

        return booking

    def update(self, instance, validated_data):
        additional_services = validated_data.pop('additional_services', None)
        instance = super().update(instance, validated_data)

        if additional_services is not None:
            instance.additional_services.set(additional_services)
            # signal handles recalculation

        return instance
    
    def validate(self, data):
        service_type = data.get('main_service')
        property_size = data.get('property_size')

        if (service_type == 'cleaning' or service_type == 'fumigation') and not property_size:
            raise serializers.ValidationError({
                "property_size": "This service type requires a property size."
            })
        return data


class BookingListSerializer(serializers.ModelSerializer):
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
        payment = obj.payments.order_by('-created_at').first()
        if not payment:
            return 'unpaid'
        return payment.status