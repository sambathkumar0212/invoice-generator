from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Company, CompanyMember
from invoice_management.forms import CompanySettingsForm


def company_setup_view(request):
    """Setup company for new users who don't belong to any company"""
    if request.user.is_authenticated and request.user.get_company():
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CompanySettingsForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.slug = company.name.lower().replace(' ', '-').replace('_', '-')
            company.save()
            
            # Create company membership for current user
            CompanyMember.objects.create(
                user=request.user,
                company=company,
                role='admin'
            )
            
            messages.success(request, f"Company '{company.name}' created successfully!")
            return redirect('dashboard')
    else:
        form = CompanySettingsForm()
    
    return render(request, 'companies/setup.html', {'form': form})


@login_required
def company_settings_view(request):
    """Manage company settings"""
    if not request.company:
        return redirect('company_setup')
    
    if request.method == 'POST':
        form = CompanySettingsForm(request.POST, instance=request.company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company settings updated successfully!')
            return redirect('companies:company_settings')
    else:
        form = CompanySettingsForm(instance=request.company)
    
    return render(request, 'companies/settings.html', {'form': form})
