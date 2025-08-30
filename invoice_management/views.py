from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.forms import inlineformset_factory
import json

from .models import Invoice, InvoiceItem, Client
from .forms import InvoiceForm, ClientForm, InvoiceItemFormSet, InvoiceItemForm
from pdf_generator import PDFInvoiceGenerator


@login_required
def dashboard_view(request):
    """Main dashboard showing invoice overview"""
    if not request.company:
        return redirect('company_setup')
    
    # Get recent invoices
    recent_invoices = Invoice.objects.filter(
        company=request.company
    ).select_related('client').order_by('-created_at')[:5]
    
    # Get statistics
    total_invoices = Invoice.objects.filter(company=request.company).count()
    total_clients = Client.objects.filter(company=request.company, is_active=True).count()
    pending_invoices = Invoice.objects.filter(
        company=request.company, 
        status='sent'
    ).count()
    overdue_invoices = Invoice.objects.filter(
        company=request.company,
        status='sent',
        due_date__lt=timezone.now().date()
    ).count()
    
    context = {
        'recent_invoices': recent_invoices,
        'total_invoices': total_invoices,
        'total_clients': total_clients,
        'pending_invoices': pending_invoices,
        'overdue_invoices': overdue_invoices,
    }
    
    return render(request, 'dashboard/index.html', context)


@login_required
def invoice_list_view(request):
    """List all invoices for the company"""
    if not request.company:
        return redirect('company_setup')
    
    invoices = Invoice.objects.filter(
        company=request.company
    ).select_related('client').order_by('-created_at')
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        invoices = invoices.filter(status=status)
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search) |
            Q(client__name__icontains=search) |
            Q(client__email__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(invoices, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status': status,
        'search': search,
    }
    
    return render(request, 'invoices/list.html', context)


@login_required
def invoice_create_view(request):
    """Create a new invoice"""
    if not request.company:
        return redirect('company_setup')
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST, company=request.company)
        formset = InvoiceItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)
            invoice.company = request.company
            invoice.created_by = request.user
            invoice.save()
            
            # Save invoice items
            for item_form in formset:
                if item_form.cleaned_data:
                    item = item_form.save(commit=False)
                    item.invoice = invoice
                    item.save()
            
            messages.success(request, f'Invoice {invoice.invoice_number} created successfully!')
            return redirect('invoice_management:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm(company=request.company)
        formset = InvoiceItemFormSet()
    
    context = {
        'form': form,
        'formset': formset,
        'title': 'Create Invoice'
    }
    
    return render(request, 'invoices/form.html', context)


@login_required
def invoice_detail_view(request, pk):
    """View invoice details"""
    invoice = get_object_or_404(
        Invoice.objects.select_related('client', 'company').prefetch_related('items'),
        pk=pk,
        company=request.company
    )
    
    context = {
        'invoice': invoice,
    }
    
    return render(request, 'invoices/detail.html', context)


@login_required
def invoice_edit_view(request, pk):
    """Edit an existing invoice"""
    invoice = get_object_or_404(Invoice, pk=pk, company=request.company)
    
    # Create a custom formset with no extra forms for editing
    EditInvoiceItemFormSet = inlineformset_factory(
        Invoice, 
        InvoiceItem, 
        form=InvoiceItemForm,
        extra=0,  # No extra forms for editing
        can_delete=True
    )
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice, company=request.company)
        formset = EditInvoiceItemFormSet(request.POST, instance=invoice)
        
        if form.is_valid() and formset.is_valid():
            invoice = form.save()
            formset.save()
            
            messages.success(request, f'Invoice {invoice.invoice_number} updated successfully!')
            return redirect('invoice_management:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm(instance=invoice, company=request.company)
        formset = EditInvoiceItemFormSet(instance=invoice)
    
    context = {
        'form': form,
        'formset': formset,
        'invoice': invoice,
        'title': f'Edit Invoice {invoice.invoice_number}'
    }
    
    return render(request, 'invoices/form.html', context)


@login_required
def invoice_pdf_view(request, pk):
    """Generate and serve PDF for an invoice"""
    invoice = get_object_or_404(Invoice, pk=pk, company=request.company)
    
    # Convert Django models to the format expected by PDFInvoiceGenerator
    from invoice_models import Invoice as PDFInvoice, Client as PDFClient, InvoiceItem as PDFItem
    
    pdf_client = PDFClient(
        name=invoice.client.name,
        email=invoice.client.email,
        address=invoice.client.address,
        phone=invoice.client.phone,
        company=invoice.client.company_name
    )
    
    pdf_items = [
        PDFItem(
            description=item.description,
            quantity=float(item.quantity),
            rate=float(item.rate),
            unit=item.unit or 'each'  # Use 'each' as default if unit is empty
        )
        for item in invoice.items.all()
    ]
    
    pdf_invoice = PDFInvoice(
        invoice_number=invoice.invoice_number,
        client=pdf_client,
        items=pdf_items,
        issue_date=invoice.issue_date,
        due_date=invoice.due_date,
        business_name=invoice.company.name,
        business_address=invoice.company.address,
        business_email=invoice.company.email,
        business_phone=invoice.company.phone,
        tax_rate=float(invoice.tax_rate),
        notes=invoice.notes
    )
    
    # Generate PDF
    pdf_generator = PDFInvoiceGenerator()
    pdf_path = pdf_generator.generate_invoice(pdf_invoice)
    
    # Serve the PDF
    with open(pdf_path, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{invoice.invoice_number}.pdf"'
        return response


@login_required
def client_list_view(request):
    """List all clients for the company"""
    if not request.company:
        return redirect('company_setup')
    
    clients = Client.objects.filter(
        company=request.company,
        is_active=True
    ).order_by('name')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        clients = clients.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(company_name__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(clients, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
    }
    
    return render(request, 'clients/list.html', context)


@login_required
def client_create_view(request):
    """Create a new client"""
    if not request.company:
        return redirect('company_setup')
    
    if request.method == 'POST':
        form = ClientForm(request.POST, company=request.company)
        if form.is_valid():
            client = form.save(commit=False)
            client.company = request.company
            client.created_by = request.user
            client.save()
            
            messages.success(request, f'Client {client.name} created successfully!')
            return redirect('invoice_management:client_list')
    else:
        form = ClientForm(company=request.company)
    
    context = {
        'form': form,
        'title': 'Add New Client'
    }
    
    return render(request, 'clients/form.html', context)


@login_required
@require_http_methods(["POST"])
def invoice_status_update(request, pk):
    """Update invoice status via AJAX"""
    invoice = get_object_or_404(Invoice, pk=pk, company=request.company)
    
    data = json.loads(request.body)
    new_status = data.get('status')
    
    if new_status in dict(Invoice.STATUS_CHOICES):
        invoice.status = new_status
        invoice.save(update_fields=['status'])
        
        return JsonResponse({
            'success': True,
            'message': f'Invoice status updated to {invoice.get_status_display()}'
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid status'
    })
