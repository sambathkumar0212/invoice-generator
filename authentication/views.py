from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import User
from companies.models import Company, CompanyMember
import json


class SignUpForm(forms.ModelForm):
    """Custom signup form for user registration"""
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    company_name = forms.CharField(max_length=255, help_text="Your company name")
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")
        
        return cleaned_data


def signup_view(request):
    """Handle user signup with company creation"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Create user
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_company_admin = True
            user.save()
            
            # Create company
            company = Company.objects.create(
                name=form.cleaned_data['company_name'],
                slug=form.cleaned_data['company_name'].lower().replace(' ', '-'),
                email=user.email,
                address="Enter your company address"
            )
            
            # Create company membership
            CompanyMember.objects.create(
                user=user,
                company=company,
                role='admin'
            )
            
            # Log the user in
            login(request, user)
            messages.success(request, f"Welcome! Your account and company '{company.name}' have been created.")
            return redirect('dashboard')
    else:
        form = SignUpForm()
    
    return render(request, 'auth/signup.html', {'form': form})


def login_view(request):
    """Handle user login"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'auth/login.html', {'form': form})


@login_required
def profile_view(request):
    """User profile management"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone = request.POST.get('phone', user.phone)
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    return render(request, 'auth/profile.html', {'user': request.user})
