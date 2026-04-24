from decimal import Decimal
from .models import AddOnType

# 1. Base Prices for Main Services
SERVICE_PRICES = {
    'cleaning': Decimal('15000.00'),
    'fumigation': Decimal('20000.00'),
    'laundry': Decimal('8000.00'),
}

# 2. Property Size Multipliers
# Multiplies the base price (e.g., Medium = 1.5x Base)
SIZE_MULTIPLIERS = {
    'small': Decimal('1.0'),
    'medium': Decimal('1.5'),
    'large': Decimal('2.0'),
    'commercial space': Decimal('3.0'),
}

# 3. Flat Fees
EMERGENCY_FEE = Decimal('10000.00')

# 4. Add-on Service Prices
ADDON_PRICES = {
    AddOnType.DEEP_CLEANING: Decimal('5000.00'),
    AddOnType.WINDOW_CLEANING: Decimal('3000.00'),
    AddOnType.CARPET_CLEANING: Decimal('2000.00'),
    # AddOnType.EMERGENCY: Decimal('10000.00'),
}