from django import forms
from django.forms import inlineformset_factory
from .models import Invoice, InvoiceItem, Client
from companies.models import Company


class InvoiceForm(forms.ModelForm):
    """Form for creating and editing invoices"""
    
    class Meta:
        model = Invoice
        fields = ['client', 'issue_date', 'due_date', 'tax_rate', 'notes']
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        if company:
            self.fields['client'].queryset = Client.objects.filter(
                company=company, 
                is_active=True
            ).order_by('name')
            self.fields['tax_rate'].initial = company.default_tax_rate
        
        # Add CSS classes
        for field in self.fields:
            if field != 'notes':
                self.fields[field].widget.attrs.update({'class': 'form-control'})


class InvoiceItemForm(forms.ModelForm):
    """Form for invoice items"""
    
    class Meta:
        model = InvoiceItem
        fields = ['description', 'quantity', 'rate', 'unit']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., hours, pieces, days'}),
        }


# Create formset for invoice items
InvoiceItemFormSet = inlineformset_factory(
    Invoice, 
    InvoiceItem, 
    form=InvoiceItemForm,
    extra=1,  # Reduced from 3 to 1
    can_delete=True
)


class ClientForm(forms.ModelForm):
    """Form for creating and editing clients"""
    
    class Meta:
        model = Client
        fields = [
            'name', 'email', 'phone', 'company_name', 
            'address', 'city', 'state', 'postal_code', 'country', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(555) 123-4567'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Street address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State or Province'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ZIP or Postal Code'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes about this client...'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
    
    def clean_email(self):
        """Validate that email is unique for this company"""
        email = self.cleaned_data.get('email')
        if email and self.company:
            # Check if this email already exists for this company
            existing_client = Client.objects.filter(
                company=self.company,
                email__iexact=email,
                is_active=True
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing_client.exists():
                client = existing_client.first()
                raise forms.ValidationError(
                    f'A client with email "{email}" already exists in your company: {client.name}. '
                    f'Please use a different email address or update the existing client.'
                )
        
        return email


class CompanySettingsForm(forms.ModelForm):
    """Form for updating company settings"""
    
    class Meta:
        model = Company
        fields = [
            'name', 'address', 'country', 'phone', 'email', 'website',
            'currency', 'invoice_prefix', 'default_tax_rate', 'default_payment_terms'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'country': forms.Select(attrs={'class': 'form-control', 'id': 'id_country'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'currency': forms.Select(attrs={'class': 'form-control', 'id': 'id_currency'}),
            'invoice_prefix': forms.TextInput(attrs={'class': 'form-control'}),
            'default_tax_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'default_payment_terms': forms.NumberInput(attrs={'class': 'form-control'}),
        }