from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse
from companies.models import CompanyMember


class CompanyMiddleware(MiddlewareMixin):
    """
    Middleware to handle company context for multi-tenant SaaS
    """
    
    def process_request(self, request):
        # Skip middleware for certain paths
        skip_paths = [
            '/admin/',
            '/auth/',
            '/api/auth/',
            '/static/',
            '/media/',
        ]
        
        if any(request.path.startswith(path) for path in skip_paths):
            return None
        
        # Set company context for authenticated users
        if request.user.is_authenticated:
            try:
                membership = CompanyMember.objects.select_related('company').get(
                    user=request.user, 
                    is_active=True
                )
                request.company = membership.company
                request.company_role = membership.role
            except CompanyMember.DoesNotExist:
                # User doesn't belong to any company
                request.company = None
                request.company_role = None
                
                # Redirect to company setup if not on auth pages
                if not request.path.startswith('/auth/') and not request.path.startswith('/company/'):
                    return redirect('company_setup')
        else:
            request.company = None
            request.company_role = None
        
        return None