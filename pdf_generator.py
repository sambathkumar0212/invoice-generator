"""
PDF Invoice Generator
Creates professional PDF invoices using ReportLab with improved UI and alignment.
"""

import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY

from invoice_models import Invoice


class PDFInvoiceGenerator:
    """Generates professional PDF invoices with improved UI and alignment."""
    
    def __init__(self, output_dir: str = "invoices"):
        self.output_dir = output_dir
        self.ensure_output_dir()
        
    def ensure_output_dir(self):
        """Create output directory if it doesn't exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_invoice(self, invoice: Invoice, filename: str = None) -> str:
        """Generate a professional PDF invoice with improved formatting."""
        if filename is None:
            filename = f"invoice_{invoice.invoice_number}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Create the PDF document with margins
        doc = SimpleDocTemplate(
            filepath, 
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        
        story = []
        
        # Custom styles for better appearance
        styles = self._create_custom_styles()
        
        # Header section with invoice title and number
        self._add_header(story, invoice, styles)
        
        # Invoice details section (moved to top)
        self._add_invoice_details(story, invoice, styles)
        
        # Company and client information section
        self._add_company_client_info(story, invoice, styles)
        
        # Items table
        self._add_items_table(story, invoice, styles)
        
        # Invoice summary section
        self._add_invoice_summary(story, invoice, styles)
        
        # Payment terms
        self._add_payment_terms(story, invoice, styles)
        
        # Notes section
        if invoice.notes:
            self._add_notes_section(story, invoice, styles)
        
        # Footer
        self._add_footer(story, styles)
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    def _create_custom_styles(self):
        """Create custom paragraph styles for better formatting."""
        styles = getSampleStyleSheet()
        
        # Custom styles
        styles.add(ParagraphStyle(
            name='InvoiceTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_RIGHT,
            spaceBefore=0,
            spaceAfter=20,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='InvoiceNumber',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#7f8c8d'),
            alignment=TA_RIGHT,
            spaceBefore=5,
            spaceAfter=30,
            fontName='Helvetica'
        ))
        
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceBefore=20,
            spaceAfter=10,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=colors.HexColor('#3498db'),
            borderPadding=5
        ))
        
        styles.add(ParagraphStyle(
            name='CompanyInfo',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=0,
            fontName='Helvetica',
            leading=14
        ))
        
        styles.add(ParagraphStyle(
            name='ClientInfo',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=0,
            fontName='Helvetica',
            leading=14
        ))
        
        styles.add(ParagraphStyle(
            name='InvoiceDetails',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=0,
            fontName='Helvetica',
            leading=14
        ))
        
        styles.add(ParagraphStyle(
            name='FooterText',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#7f8c8d'),
            alignment=TA_CENTER,
            spaceBefore=20,
            fontName='Helvetica-Oblique'
        ))
        
        styles.add(ParagraphStyle(
            name='TotalLabel',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='TotalAmount',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_RIGHT,
            fontName='Helvetica'
        ))
        
        styles.add(ParagraphStyle(
            name='FinalTotalLabel',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='FinalTotalAmount',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='ItemsHeader',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            textColor=colors.white,
            alignment=TA_CENTER,
            spaceAfter=6
        ))
        
        return styles
    
    def _add_header(self, story, invoice, styles):
        """Add header with invoice title and number."""
        # Header section with invoice title and number
        header_title = Paragraph('INVOICE', styles['InvoiceTitle'])
        story.append(header_title)
        
        invoice_number_text = f"Invoice #{invoice.invoice_number}"
        invoice_number = Paragraph(invoice_number_text, styles['InvoiceNumber'])
        story.append(invoice_number)
        
        story.append(Spacer(1, 20))
    
    def _add_company_client_info(self, story, invoice, styles):
        """Add company and client information section."""
        # Prepare company info
        company_lines = [
            f"<b>{invoice.business_name}</b>",
            invoice.business_address.replace('\n', '<br/>') if invoice.business_address else "",
        ]
        if invoice.business_email:
            company_lines.append(f"Email: {invoice.business_email}")
        if invoice.business_phone:
            company_lines.append(f"Phone: {invoice.business_phone}")
        
        company_info = Paragraph("<br/>".join(filter(None, company_lines)), styles['CompanyInfo'])
        
        # Prepare client info
        client_lines = [
            f"<b>{invoice.client.name}</b>",
        ]
        if hasattr(invoice.client, 'company') and invoice.client.company:
            client_lines.append(invoice.client.company)
        
        client_lines.append(invoice.client.address.replace('\n', '<br/>') if invoice.client.address else "")
        client_lines.append(f"Email: {invoice.client.email}")
        
        if hasattr(invoice.client, 'phone') and invoice.client.phone:
            client_lines.append(f"Phone: {invoice.client.phone}")
        
        client_info = Paragraph("<br/>".join(filter(None, client_lines)), styles['ClientInfo'])
        
        # Create info table
        info_data = [
            [
                Paragraph('<b>From:</b>', styles['SectionHeader']),
                '',
                Paragraph('<b>Bill To:</b>', styles['SectionHeader'])
            ],
            [company_info, '', client_info]
        ]
        
        info_table = Table(info_data, colWidths=[2.8*inch, 0.4*inch, 2.8*inch])
        info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 1), (-1, 1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 30))
    
    def _add_invoice_details(self, story, invoice, styles):
        """Add invoice details section."""
        details_data = [
            ['Invoice Date:', invoice.issue_date.strftime('%B %d, %Y')],
            ['Due Date:', invoice.due_date.strftime('%B %d, %Y')],
        ]
        
        # Check if invoice is overdue
        if invoice.due_date < datetime.now().date():
            days_overdue = (datetime.now().date() - invoice.due_date).days
            details_data.append(['Status:', f'<font color="red"><b>OVERDUE ({days_overdue} days)</b></font>'])
        
        details_table = Table(details_data, colWidths=[1.5*inch, 2*inch])
        details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        # Right-align the details table
        details_wrapper = Table([[details_table]], colWidths=[6*inch])
        details_wrapper.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        story.append(details_wrapper)
        story.append(Spacer(1, 30))
    
    def _add_items_table(self, story, invoice, styles):
        """Add items table with improved formatting and better unit spacing."""
        # Header
        section_header = Paragraph('Items & Services', styles['SectionHeader'])
        story.append(section_header)
        story.append(Spacer(1, 10))
        
        # Items table data with optimized Unit column
        items_data = [['Description', 'Qty', 'Unit', 'Rate', 'Amount']]
        
        for item in invoice.items:
            # Format quantity with proper decimal places
            qty_formatted = str(int(item.quantity)) if item.quantity.is_integer() else f"{item.quantity:.2f}"
            
            # Format unit with consistent spacing and better presentation
            unit_formatted = item.unit.strip() if item.unit and item.unit.strip() else "each"
            # Ensure proper capitalization and spacing for common units
            unit_display_map = {
                'hour': 'hr',
                'hours': 'hrs', 
                'day': 'day',
                'days': 'days',
                'piece': 'pc',
                'pieces': 'pcs',
                'each': 'each',
                'item': 'item',
                'unit': 'unit',
                'box': 'box',
                'kg': 'kg',
                'lb': 'lb',
                'meter': 'm',
                'foot': 'ft',
                'inch': 'in'
            }
            unit_formatted = unit_display_map.get(unit_formatted.lower(), unit_formatted)
            
            items_data.append([
                item.description,
                qty_formatted,
                unit_formatted,
                f"${item.rate:.2f}",
                f"${item.total:.2f}"
            ])
        
        # Optimized column widths for better unit spacing and visual balance
        items_table = Table(items_data, colWidths=[2.8*inch, 0.7*inch, 0.9*inch, 1.0*inch, 1.2*inch])
        items_table.setStyle(TableStyle([
            # Header row styling with enhanced appearance
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 14),
            ('TOPPADDING', (0, 0), (-1, 0), 14),
            
            # Data rows styling with improved spacing
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 12),
            ('LEFTPADDING', (0, 1), (-1, -1), 10),
            ('RIGHTPADDING', (0, 1), (-1, -1), 10),
            
            # Alignment with improved unit column spacing
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),     # Description
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),   # Quantity
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),   # Unit - centered for better readability
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),    # Rate
            ('ALIGN', (4, 0), (4, -1), 'RIGHT'),    # Amount
            
            # Enhanced borders and spacing
            ('GRID', (0, 0), (-1, 0), 1, colors.HexColor('#3498db')),  # Header border
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#3498db')),
            ('INNERGRID', (0, 1), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#34495e')),
            
            # Alternating row colors for better readability
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            
            # Vertical alignment
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Special styling for unit column to make it stand out with better spacing
            ('FONTNAME', (2, 1), (2, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (2, 1), (2, -1), colors.HexColor('#2c3e50')),
            ('BACKGROUND', (2, 1), (2, -1), colors.HexColor('#ecf0f1')),
            
            # Enhanced spacing for unit column
            ('LEFTPADDING', (2, 1), (2, -1), 12),
            ('RIGHTPADDING', (2, 1), (2, -1), 12),
            
            # Better visual separation for the unit column
            ('LINEAFTER', (1, 0), (1, -1), 1, colors.HexColor('#bdc3c7')),
            ('LINEAFTER', (2, 0), (2, -1), 1, colors.HexColor('#bdc3c7')),
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 20))
    
    def _add_invoice_summary(self, story, invoice, styles):
        """Add invoice summary with improved spacing to match unit details formatting."""
        # Calculate totals
        subtotal = sum(item.total for item in invoice.items)
        tax_amount = subtotal * (invoice.tax_rate / 100) if invoice.tax_rate else 0
        total = subtotal + tax_amount
        
        # Summary data with better spacing and alignment
        summary_data = []
        
        # Add subtotal
        summary_data.append(['', '', 'Subtotal:', f"${subtotal:.2f}"])
        
        # Add tax if applicable
        if invoice.tax_rate and invoice.tax_rate > 0:
            summary_data.append(['', '', f'Tax ({invoice.tax_rate}%):', f"${tax_amount:.2f}"])
        
        # Add total with emphasis
        summary_data.append(['', '', 'Total:', f"${total:.2f}"])
        
        # Create summary table with optimized spacing
        summary_table = Table(summary_data, colWidths=[3.0*inch, 0.6*inch, 1.8*inch, 1.2*inch])
        summary_table.setStyle(TableStyle([
            # General formatting
            ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -2), 10),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),  # Total row bold
            ('FONTSIZE', (0, -1), (-1, -1), 12),  # Total row larger
            
            # Alignment to match items table
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),   # Labels right-aligned
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),   # Values right-aligned
            
            # Padding for better spacing
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            
            # Borders for summary section
            ('LINEABOVE', (2, -1), (-1, -1), 2, colors.HexColor('#3498db')),  # Line above total
            ('LINEBELOW', (2, -1), (-1, -1), 2, colors.HexColor('#3498db')),  # Line below total
            
            # Background for total row
            ('BACKGROUND', (2, -1), (-1, -1), colors.HexColor('#ecf0f1')),
            
            # Text color for total
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#2c3e50')),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
    
    def _add_notes_section(self, story, invoice, styles):
        """Add notes section."""
        notes_header = Paragraph('Notes:', styles['SectionHeader'])
        story.append(notes_header)
        
        notes_text = Paragraph(invoice.notes, styles['Normal'])
        story.append(notes_text)
        story.append(Spacer(1, 20))
    
    def _add_payment_terms(self, story, invoice, styles):
        """Add payment terms section."""
        # Add payment terms if specified
        payment_terms = getattr(invoice, 'payment_terms', None)
        if not payment_terms:
            # Default payment terms based on due date
            days_to_pay = (invoice.due_date - invoice.issue_date).days
            if days_to_pay <= 0:
                payment_terms = "Payment due upon receipt"
            elif days_to_pay <= 15:
                payment_terms = f"Payment due within {days_to_pay} days"
            else:
                payment_terms = f"Payment due within {days_to_pay} days of invoice date"
        
        terms_header = Paragraph('Payment Terms:', styles['SectionHeader'])
        story.append(terms_header)
        
        terms_text = Paragraph(payment_terms, styles['Normal'])
        story.append(terms_text)
        story.append(Spacer(1, 15))
    
    def _add_footer(self, story, styles):
        """Add footer with professional touch and contact information."""
        # Add payment terms before footer
        story.append(Spacer(1, 20))
        
        # Contact information in footer
        footer_lines = []
        footer_lines.append('Thank you for your business!')
        footer_lines.append('Questions about this invoice? Contact us at:')
        
        # Add business contact info if available
        contact_info = []
        if hasattr(self, 'business_email'):
            contact_info.append(f"Email: {self.business_email}")
        if hasattr(self, 'business_phone'):
            contact_info.append(f"Phone: {self.business_phone}")
        
        if contact_info:
            footer_lines.append(' | '.join(contact_info))
        
        footer_text = Paragraph(
            '<br/>'.join(footer_lines), 
            styles['FooterText']
        )
        story.append(Spacer(1, 30))
        story.append(footer_text)
    
    def _add_watermark(self, canvas, doc):
        """Add watermark for unpaid invoices."""
        # This would be called if invoice is overdue
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 50)
        canvas.setFillColor(colors.red, alpha=0.1)
        canvas.rotate(45)
        canvas.drawCentredText(400, 100, 'OVERDUE')
        canvas.restoreState()
    
    def generate_invoice_with_advanced_features(self, invoice: Invoice, filename: str = None, 
                                              add_watermark: bool = False) -> str:
        """Generate a professional PDF invoice with advanced features."""
        if filename is None:
            filename = f"invoice_{invoice.invoice_number}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Create the PDF document with margins
        doc = SimpleDocTemplate(
            filepath, 
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=60  # More space for footer
        )
        
        story = []
        
        # Custom styles for better appearance
        styles = self._create_custom_styles()
        
        # Header section with invoice title and number
        self._add_header(story, invoice, styles)
        
        # Invoice details section (moved to top)
        self._add_invoice_details(story, invoice, styles)
        
        # Company and client information section
        self._add_company_client_info(story, invoice, styles)
        
        # Items table
        self._add_items_table(story, invoice, styles)
        
        # Invoice summary section
        self._add_invoice_summary(story, invoice, styles)
        
        # Payment terms
        self._add_payment_terms(story, invoice, styles)
        
        # Notes section
        if invoice.notes:
            self._add_notes_section(story, invoice, styles)
        
        # Footer
        self._add_footer(story, styles)
        
        # Build PDF with optional watermark
        if add_watermark and invoice.due_date < datetime.now().date():
            doc.build(story, onFirstPage=self._add_watermark, onLaterPages=self._add_watermark)
        else:
            doc.build(story)
        
        return filepath