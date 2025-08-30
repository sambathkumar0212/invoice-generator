"""
Invoice Generator - Core Classes
A professional invoice generation system for small businesses and freelancers.
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from decimal import Decimal


@dataclass
class Client:
    """Client information for invoicing."""
    name: str
    email: str
    address: str
    phone: Optional[str] = None
    company: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Client':
        return cls(**data)


@dataclass
class InvoiceItem:
    """Individual item/service on an invoice."""
    description: str
    quantity: float
    rate: float
    unit: str = "hours"  # Default unit, can be hours, pieces, days, kg, etc.
    
    @property
    def total(self) -> float:
        return round(self.quantity * self.rate, 2)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'InvoiceItem':
        return cls(**data)


@dataclass
class Invoice:
    """Main invoice class containing all invoice data."""
    invoice_number: str
    client: Client
    items: List[InvoiceItem]
    issue_date: datetime
    due_date: datetime
    business_name: str
    business_address: str
    business_email: str
    business_phone: Optional[str] = None
    tax_rate: float = 0.0
    notes: Optional[str] = None
    payment_terms: Optional[str] = None
    currency: str = "USD"
    status: str = "pending"  # pending, paid, overdue, cancelled
    discount_percentage: float = 0.0
    
    @property
    def subtotal(self) -> float:
        return round(sum(item.total for item in self.items), 2)
    
    @property
    def discount_amount(self) -> float:
        return round(self.subtotal * self.discount_percentage / 100, 2)
    
    @property
    def subtotal_after_discount(self) -> float:
        return round(self.subtotal - self.discount_amount, 2)
    
    @property
    def tax_amount(self) -> float:
        return round(self.subtotal_after_discount * self.tax_rate / 100, 2)
    
    @property
    def total(self) -> float:
        return round(self.subtotal_after_discount + self.tax_amount, 2)
    
    @property
    def is_overdue(self) -> bool:
        """Check if invoice is overdue."""
        return self.due_date.date() < datetime.now().date() and self.status == "pending"
    
    @property
    def days_until_due(self) -> int:
        """Calculate days until due date."""
        return (self.due_date.date() - datetime.now().date()).days
    
    def get_currency_symbol(self) -> str:
        """Get currency symbol for display."""
        currency_symbols = {
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "CAD": "C$",
            "AUD": "A$",
            "JPY": "¥"
        }
        return currency_symbols.get(self.currency, "$")
    
    def format_amount(self, amount: float) -> str:
        """Format amount with currency symbol."""
        symbol = self.get_currency_symbol()
        return f"{symbol}{amount:,.2f}"
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        data['issue_date'] = self.issue_date.isoformat()
        data['due_date'] = self.due_date.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Invoice':
        # Convert ISO format strings back to datetime objects
        data['issue_date'] = datetime.fromisoformat(data['issue_date'])
        data['due_date'] = datetime.fromisoformat(data['due_date'])
        data['client'] = Client.from_dict(data['client'])
        data['items'] = [InvoiceItem.from_dict(item) for item in data['items']]
        return cls(**data)