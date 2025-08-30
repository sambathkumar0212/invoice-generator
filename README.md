# Invoice Generator

A professional invoice generation system for small businesses and freelancers that replaces expensive SaaS solutions like Freshbooks. Generate beautiful PDF invoices with automatic calculations, client management, and professional formatting.

## Features

- **Professional PDF Generation**: Create beautiful, professional invoices using ReportLab
- **Client Management**: Store and manage client information with JSON-based storage
- **Automatic Calculations**: Automatic subtotal, tax, and total calculations
- **Invoice Numbering**: Automatic sequential invoice numbering
- **Tax Support**: Configurable tax rates per invoice
- **Professional Templates**: Clean, business-ready invoice layouts
- **Command Line Interface**: Easy-to-use CLI for all operations
- **Cost Effective**: No monthly subscriptions - run locally

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Make the main script executable (optional):**
   ```bash
   chmod +x invoice_generator.py
   ```

## Quick Start

### 1. Set up your business information
```bash
python invoice_generator.py setup
```

### 2. Add your first client
```bash
python invoice_generator.py add-client
```

### 3. Create your first invoice
```bash
python invoice_generator.py create-invoice
```

### 4. List all clients
```bash
python invoice_generator.py list-clients
```

## Usage Examples

### Business Setup
When you first run the setup command, you'll be prompted to enter your business details:
```bash
python invoice_generator.py setup
```

### Adding Clients
Add new clients with their contact information:
```bash
python invoice_generator.py add-client
```

### Creating Invoices
The invoice creation process is interactive and guides you through:
- Selecting a client
- Setting due date
- Adding items/services with quantities and rates
- Adding optional notes
- Automatic PDF generation

## File Structure

```
Invoice_generator/
├── invoice_generator.py    # Main application
├── invoice_models.py       # Data models (Invoice, Client, InvoiceItem)
├── pdf_generator.py        # PDF generation using ReportLab
├── client_manager.py       # Client data management
├── requirements.txt        # Python dependencies
├── config.json            # Business configuration (auto-generated)
├── data/                  # Client data storage
│   └── clients.json       # Client database
└── invoices/              # Generated PDF invoices
    └── invoice_*.pdf      # Your invoice PDFs
```

## Configuration

The system automatically creates a `config.json` file with your business information:

```json
{
  "business_name": "Your Business Name",
  "business_address": "123 Business St\nCity, State 12345",
  "business_email": "contact@yourbusiness.com",
  "business_phone": "(555) 123-4567",
  "default_tax_rate": 0.0,
  "invoice_counter": 1
}
```

## Sample Invoice Output

The generated invoices include:
- Professional header with "INVOICE" title
- Business and client information in organized sections
- Itemized services/products table with quantities, rates, and totals
- Automatic subtotal, tax, and total calculations
- Due date and invoice number
- Optional notes section
- Clean, professional formatting suitable for business use

## Cost Comparison

| Feature | This Solution | Freshbooks | QuickBooks |
|---------|---------------|------------|------------|
| Monthly Cost | $0 | $15-50+ | $25-180+ |
| Setup Cost | Free | $0 | $0 |
| Invoice Generation | ✅ | ✅ | ✅ |
| Client Management | ✅ | ✅ | ✅ |
| PDF Export | ✅ | ✅ | ✅ |
| Local Storage | ✅ | ❌ | ❌ |
| No Internet Required | ✅ | ❌ | ❌ |
| Customizable | ✅ | Limited | Limited |

## Advanced Usage

### Customizing Invoice Templates
You can modify `pdf_generator.py` to customize:
- Colors and fonts
- Layout and spacing
- Logo placement
- Additional fields

### Data Backup
Client data is stored in `data/clients.json` and business config in `config.json`. 
Simply backup these files to preserve your data.

### Integration
The modular design allows easy integration with other Python applications:

```python
from invoice_generator import InvoiceGenerator
from invoice_models import Client, InvoiceItem

# Create invoice programmatically
app = InvoiceGenerator()
client = Client(name="John Doe", email="john@example.com", address="123 Main St")
# ... continue with invoice creation
```

## Requirements

- Python 3.7+
- ReportLab (for PDF generation)
- Pillow (for image handling)
- python-dateutil (for date handling)

## License

This project is open source and available under the MIT License.

## Support

This is a self-contained solution designed for simplicity and cost-effectiveness. For customization or additional features, you can modify the Python source code to meet your specific needs.