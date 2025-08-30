from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model that extends Django's AbstractUser
    for company-based SaaS authentication
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    is_company_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'auth_user'
        
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_company(self):
        """Get the company this user belongs to"""
        from companies.models import CompanyMember
        try:
            membership = CompanyMember.objects.get(user=self)
            return membership.company
        except CompanyMember.DoesNotExist:
            return None
