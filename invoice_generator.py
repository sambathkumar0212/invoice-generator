#!/usr/bin/env python3
"""
Invoice Generator - Main Application
A professional invoice generation system for small businesses and freelancers.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from typing import List

from invoice_models import Client, Invoice, InvoiceItem
from client_manager import ClientManager
from pdf_generator import PDFInvoiceGenerator


class InvoiceGenerator:
    """Main invoice generator application."""
    
    def __init__(self):
        self.client_manager = ClientManager()
        self.pdf_generator = PDFInvoiceGenerator()
        self.config_file = "config.json"
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        """Load business configuration from file."""
        default_config = {
            "business_name": "Your Business Name",
            "business_address": "123 Business St\nCity, State 12345",
            "business_email": "contact@yourbusiness.com",
            "business_phone": "(555) 123-4567",
            "default_tax_rate": 0.0,
            "invoice_counter": 1
        }
        
        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return default_config
    
    def save_config(self):
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_next_invoice_number(self) -> str:
        """Generate next invoice number."""
        invoice_num = f"INV-{self.config['invoice_counter']:04d}"
        self.config['invoice_counter'] += 1
        self.save_config()
        return invoice_num
    
    def setup_business(self):
        """Interactive business setup."""
        print("\n=== Business Information Setup ===")
        
        self.config['business_name'] = input(f"Business Name [{self.config['business_name']}]: ").strip() or self.config['business_name']
        self.config['business_address'] = input(f"Business Address [{self.config['business_address']}]: ").strip() or self.config['business_address']
        self.config['business_email'] = input(f"Business Email [{self.config['business_email']}]: ").strip() or self.config['business_email']
        self.config['business_phone'] = input(f"Business Phone [{self.config['business_phone']}]: ").strip() or self.config['business_phone']
        
        try:
            tax_rate = float(input(f"Default Tax Rate % [{self.config['default_tax_rate']}]: ").strip() or self.config['default_tax_rate'])
            self.config['default_tax_rate'] = tax_rate
        except ValueError:
            print("Invalid tax rate, keeping current value.")
        
        self.save_config()
        print("Business information updated successfully!")
    
    def add_client_interactive(self):
        """Interactive client addition."""
        print("\n=== Add New Client ===")
        
        name = input("Client Name: ").strip()
        if not name:
            print("Client name is required!")
            return
        
        email = input("Client Email: ").strip()
        if not email:
            print("Client email is required!")
            return
        
        address = input("Client Address: ").strip()
        if not address:
            print("Client address is required!")
            return
        
        phone = input("Client Phone (optional): ").strip() or None
        company = input("Company Name (optional): ").strip() or None
        
        client = Client(name=name, email=email, address=address, phone=phone, company=company)
        
        if self.client_manager.add_client(client):
            print(f"Client '{name}' added successfully!")
        else:
            print(f"Client with email '{email}' already exists!")
    
    def list_clients(self):
        """List all clients."""
        clients = self.client_manager.list_clients()
        
        if not clients:
            print("No clients found.")
            return
        
        print("\n=== Client List ===")
        for i, client in enumerate(clients, 1):
            print(f"{i}. {client.name} ({client.email})")
            if client.company:
                print(f"   Company: {client.company}")
            print(f"   Address: {client.address}")
            if client.phone:
                print(f"   Phone: {client.phone}")
            print()
    
    def create_invoice_interactive(self):
        """Interactive invoice creation."""
        print("\n=== Create New Invoice ===")
        
        # Select client
        clients = self.client_manager.list_clients()
        if not clients:
            print("No clients found. Please add a client first.")
            return
        
        print("Select a client:")
        for i, client in enumerate(clients, 1):
            print(f"{i}. {client.name} ({client.email})")
        
        try:
            client_idx = int(input("Enter client number: ")) - 1
            if client_idx < 0 or client_idx >= len(clients):
                print("Invalid client selection!")
                return
            selected_client = clients[client_idx]
        except ValueError:
            print("Invalid input!")
            return
        
        # Get invoice details
        invoice_number = self.get_next_invoice_number()
        print(f"Invoice Number: {invoice_number}")
        
        issue_date = datetime.now()
        
        # Due date
        try:
            days_until_due = int(input("Days until due (default 30): ").strip() or "30")
            due_date = issue_date + timedelta(days=days_until_due)
        except ValueError:
            due_date = issue_date + timedelta(days=30)
        
        # Currency
        print("Available currencies: USD, EUR, GBP, CAD, AUD, JPY")
        currency = input("Currency (default USD): ").strip().upper() or "USD"
        if currency not in ["USD", "EUR", "GBP", "CAD", "AUD", "JPY"]:
            print("Invalid currency, using USD")
            currency = "USD"
        
        # Payment terms
        payment_terms = input("Payment terms (e.g., 'Net 30', 'Due on receipt'): ").strip() or None
        
        # Tax rate
        try:
            tax_rate = float(input(f"Tax rate % (default {self.config['default_tax_rate']}): ").strip() or self.config['default_tax_rate'])
        except ValueError:
            tax_rate = self.config['default_tax_rate']
        
        # Discount
        try:
            discount = float(input("Discount % (default 0): ").strip() or "0")
        except ValueError:
            discount = 0.0
        
        # Items
        items = []
        print("\nEnter invoice items (press Enter with empty description to finish):")
        
        while True:
            description = input("Item description: ").strip()
            if not description:
                break
            
            try:
                quantity = float(input("Quantity: "))
                rate = float(input("Rate: "))
                unit = input("Unit (e.g., 'hours', 'items', 'each') [default: each]: ").strip() or "each"
                items.append(InvoiceItem(description=description, quantity=quantity, rate=rate, unit=unit))
                print(f"Added: {description} - {quantity} {unit} x {rate:.2f} = {quantity * rate:.2f}")
            except ValueError:
                print("Invalid quantity or rate!")
                continue
        
        if not items:
            print("No items added. Invoice not created.")
            return
        
        # Notes
        notes = input("Notes (optional): ").strip() or None
        
        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            client=selected_client,
            items=items,
            issue_date=issue_date,
            due_date=due_date,
            business_name=self.config['business_name'],
            business_address=self.config['business_address'],
            business_email=self.config['business_email'],
            business_phone=self.config['business_phone'],
            tax_rate=tax_rate,
            notes=notes,
            currency=currency,
            payment_terms=payment_terms,
            discount_percentage=discount
        )
        
        # Generate PDF
        try:
            pdf_path = self.pdf_generator.generate_invoice(invoice)
            print(f"\nInvoice created successfully!")
            print(f"PDF saved to: {pdf_path}")
            print(f"Subtotal: {invoice.format_amount(invoice.subtotal)}")
            if invoice.discount_percentage > 0:
                print(f"Discount ({invoice.discount_percentage}%): -{invoice.format_amount(invoice.discount_amount)}")
            if invoice.tax_rate > 0:
                print(f"Tax ({invoice.tax_rate}%): {invoice.format_amount(invoice.tax_amount)}")
            print(f"Total: {invoice.format_amount(invoice.total)}")
            if invoice.payment_terms:
                print(f"Payment Terms: {invoice.payment_terms}")
        except Exception as e:
            print(f"Error generating PDF: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description="Professional Invoice Generator")
    parser.add_argument('command', choices=['setup', 'add-client', 'list-clients', 'create-invoice'], 
                       help='Command to execute')
    
    args = parser.parse_args()
    
    app = InvoiceGenerator()
    
    if args.command == 'setup':
        app.setup_business()
    elif args.command == 'add-client':
        app.add_client_interactive()
    elif args.command == 'list-clients':
        app.list_clients()
    elif args.command == 'create-invoice':
        app.create_invoice_interactive()


if __name__ == "__main__":
    main()