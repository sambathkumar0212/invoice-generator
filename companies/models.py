from django.db import models
from django.conf import settings


class Company(models.Model):
    """
    Company model for multi-tenant SaaS architecture
    """
    # Country choices with common countries
    COUNTRY_CHOICES = [
        ('US', 'United States'),
        ('CA', 'Canada'),
        ('GB', 'United Kingdom'),
        ('AU', 'Australia'),
        ('DE', 'Germany'),
        ('FR', 'France'),
        ('IT', 'Italy'),
        ('ES', 'Spain'),
        ('NL', 'Netherlands'),
        ('BE', 'Belgium'),
        ('CH', 'Switzerland'),
        ('AT', 'Austria'),
        ('SE', 'Sweden'),
        ('NO', 'Norway'),
        ('DK', 'Denmark'),
        ('FI', 'Finland'),
        ('IE', 'Ireland'),
        ('PT', 'Portugal'),
        ('IN', 'India'),
        ('SG', 'Singapore'),
        ('HK', 'Hong Kong'),
        ('JP', 'Japan'),
        ('CN', 'China'),
        ('BR', 'Brazil'),
        ('MX', 'Mexico'),
        ('NZ', 'New Zealand'),
        ('ZA', 'South Africa'),
    ]
    
    # Currency choices
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar ($)'),
        ('EUR', 'Euro (€)'),
        ('GBP', 'British Pound (£)'),
        ('CAD', 'Canadian Dollar (C$)'),
        ('AUD', 'Australian Dollar (A$)'),
        ('CHF', 'Swiss Franc (CHF)'),
        ('SEK', 'Swedish Krona (kr)'),
        ('NOK', 'Norwegian Krone (kr)'),
        ('DKK', 'Danish Krone (kr)'),
        ('JPY', 'Japanese Yen (¥)'),
        ('CNY', 'Chinese Yuan (¥)'),
        ('INR', 'Indian Rupee (₹)'),
        ('SGD', 'Singapore Dollar (S$)'),
        ('HKD', 'Hong Kong Dollar (HK$)'),
        ('BRL', 'Brazilian Real (R$)'),
        ('MXN', 'Mexican Peso ($)'),
        ('NZD', 'New Zealand Dollar (NZ$)'),
        ('ZAR', 'South African Rand (R)'),
    ]
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    address = models.TextField()
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, default='US')
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    
    # Currency settings
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    
    # Invoice settings
    invoice_prefix = models.CharField(max_length=10, default='INV')
    invoice_counter = models.PositiveIntegerField(default=1)
    default_tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    default_payment_terms = models.PositiveIntegerField(default=30, help_text="Days until payment is due")
    
    # Subscription/billing
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_currency_symbol(self):
        """Get currency symbol based on selected currency"""
        currency_symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'CAD': 'C$',
            'AUD': 'A$',
            'CHF': 'CHF',
            'SEK': 'kr',
            'NOK': 'kr',
            'DKK': 'kr',
            'JPY': '¥',
            'CNY': '¥',
            'INR': '₹',
            'SGD': 'S$',
            'HKD': 'HK$',
            'BRL': 'R$',
            'MXN': '$',
            'NZD': 'NZ$',
            'ZAR': 'R',
        }
        return currency_symbols.get(self.currency, '$')
    
    def get_country_currency_mapping(self):
        """Get default currency for selected country"""
        country_currency_map = {
            'US': 'USD',
            'CA': 'CAD',
            'GB': 'GBP',
            'AU': 'AUD',
            'DE': 'EUR',
            'FR': 'EUR',
            'IT': 'EUR',
            'ES': 'EUR',
            'NL': 'EUR',
            'BE': 'EUR',
            'CH': 'CHF',
            'AT': 'EUR',
            'SE': 'SEK',
            'NO': 'NOK',
            'DK': 'DKK',
            'FI': 'EUR',
            'IE': 'EUR',
            'PT': 'EUR',
            'IN': 'INR',
            'SG': 'SGD',
            'HK': 'HKD',
            'JP': 'JPY',
            'CN': 'CNY',
            'BR': 'BRL',
            'MX': 'MXN',
            'NZ': 'NZD',
            'ZA': 'ZAR',
        }
        return country_currency_map.get(self.country, 'USD')
    
    def get_next_invoice_number(self):
        """Generate the next invoice number for this company"""
        invoice_number = f"{self.invoice_prefix}-{self.invoice_counter:04d}"
        self.invoice_counter += 1
        self.save(update_fields=['invoice_counter'])
        return invoice_number


class CompanyMember(models.Model):
    """
    Membership model linking users to companies with roles
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
        ('viewer', 'Viewer'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['user', 'company']
        ordering = ['joined_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.company.name} ({self.role})"


class CompanyInvitation(models.Model):
    """
    Model for inviting users to join a company
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    email = models.EmailField()
    role = models.CharField(max_length=10, choices=CompanyMember.ROLE_CHOICES, default='user')
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        unique_together = ['company', 'email']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invitation to {self.email} for {self.company.name}"
