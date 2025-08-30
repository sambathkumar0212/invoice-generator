from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal


class Client(models.Model):
    """
    Client model for storing customer information per company
    """
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='clients')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    
    # Address fields
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True, default='United States')
    
    # Additional information
    notes = models.TextField(blank=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['company', 'email']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.email})"


class Invoice(models.Model):
    """
    Invoice model adapted for multi-tenant SaaS architecture
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=50)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices')
    
    # Dates
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    
    # Financial details
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True)
    
    # Status and tracking
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # PDF file
    pdf_file = models.FileField(upload_to='invoices/', blank=True, null=True)
    
    class Meta:
        unique_together = ['company', 'invoice_number']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.invoice_number} - {self.client.name}"
    
    @property
    def subtotal(self):
        """Calculate subtotal from all invoice items"""
        return sum(item.total for item in self.items.all())
    
    @property
    def tax_amount(self):
        """Calculate tax amount"""
        return (self.subtotal * self.tax_rate / 100).quantize(Decimal('0.01'))
    
    @property
    def total(self):
        """Calculate total amount including tax"""
        return (self.subtotal + self.tax_amount).quantize(Decimal('0.01'))
    
    @property
    def is_overdue(self):
        """Check if invoice is overdue"""
        return self.due_date < timezone.now().date() and self.status in ['sent']
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.company.get_next_invoice_number()
        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    """
    Individual items/services on an invoice
    """
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1.00'))
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default='hours', help_text='Unit of measurement (e.g., hours, pieces, days, kg)')
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.description} ({self.invoice.invoice_number})"
    
    @property
    def total(self):
        """Calculate total for this item"""
        return (self.quantity * self.rate).quantize(Decimal('0.01'))


class InvoiceTemplate(models.Model):
    """
    Invoice templates for companies to customize their invoice appearance
    """
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='invoice_templates')
    name = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    
    # Template customization options
    primary_color = models.CharField(max_length=7, default='#3498db')  # Hex color
    secondary_color = models.CharField(max_length=7, default='#2c3e50')
    font_family = models.CharField(max_length=50, default='Helvetica')
    logo_position = models.CharField(
        max_length=10, 
        choices=[('left', 'Left'), ('center', 'Center'), ('right', 'Right')],
        default='left'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['company', 'name']
        ordering = ['-is_default', 'name']
    
    def __str__(self):
        return f"{self.company.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        if self.is_default:
            # Ensure only one default template per company
            InvoiceTemplate.objects.filter(
                company=self.company, 
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
