#!/usr/bin/env python3
"""
Client Manager for Invoice Generation System
Manages client information and provides CRUD operations
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class ClientManager:
    def __init__(self, data_file="data/clients.json"):
        self.data_file = data_file
        self.ensure_data_directory()
        self.clients = self.load_clients()
    
    def ensure_data_directory(self):
        """Ensure the data directory exists"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
    
    def load_clients(self) -> List[Dict]:
        """Load clients from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def save_clients(self):
        """Save clients to JSON file"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.clients, f, indent=2, ensure_ascii=False)
    
    def add_client(self, client_data: Dict) -> str:
        """Add a new client and return the client ID"""
        # Generate unique client ID
        client_id = self.generate_client_id()
        
        # Add metadata
        client_data['id'] = client_id
        client_data['created_date'] = datetime.now().isoformat()
        client_data['last_modified'] = datetime.now().isoformat()
        
        # Validate required fields
        required_fields = ['name', 'email']
        for field in required_fields:
            if not client_data.get(field):
                raise ValueError(f"Required field '{field}' is missing")
        
        # Add default values for optional fields
        defaults = {
            'company': '',
            'address': '',
            'city': '',
            'state': '',
            'postal_code': '',
            'country': '',
            'phone': '',
            'website': '',
            'tax_id': '',
            'payment_terms': 'Net 30',
            'currency': 'USD',
            'notes': '',
            'billing_address': '',
            'is_active': True
        }
        
        for key, default_value in defaults.items():
            if key not in client_data:
                client_data[key] = default_value
        
        self.clients.append(client_data)
        self.save_clients()
        return client_id
    
    def generate_client_id(self) -> str:
        """Generate a unique client ID"""
        if not self.clients:
            return "CL-001"
        
        # Find the highest existing ID number
        max_num = 0
        for client in self.clients:
            client_id = client.get('id', '')
            if client_id.startswith('CL-'):
                try:
                    num = int(client_id.split('-')[1])
                    max_num = max(max_num, num)
                except (IndexError, ValueError):
                    continue
        
        return f"CL-{max_num + 1:03d}"
    
    def get_client(self, client_id: str) -> Optional[Dict]:
        """Get a client by ID"""
        for client in self.clients:
            if client.get('id') == client_id:
                return client.copy()
        return None
    
    def get_client_by_email(self, email: str) -> Optional[Dict]:
        """Get a client by email address"""
        for client in self.clients:
            if client.get('email', '').lower() == email.lower():
                return client.copy()
        return None
    
    def update_client(self, client_id: str, updates: Dict) -> bool:
        """Update a client's information"""
        for i, client in enumerate(self.clients):
            if client.get('id') == client_id:
                # Don't allow updating certain fields
                protected_fields = ['id', 'created_date']
                for field in protected_fields:
                    updates.pop(field, None)
                
                # Update last modified timestamp
                updates['last_modified'] = datetime.now().isoformat()
                
                # Update the client
                self.clients[i].update(updates)
                self.save_clients()
                return True
        return False
    
    def delete_client(self, client_id: str) -> bool:
        """Delete a client (soft delete by marking inactive)"""
        for client in self.clients:
            if client.get('id') == client_id:
                client['is_active'] = False
                client['last_modified'] = datetime.now().isoformat()
                self.save_clients()
                return True
        return False
    
    def list_clients(self, active_only: bool = True) -> List[Dict]:
        """List all clients"""
        if active_only:
            return [client for client in self.clients if client.get('is_active', True)]
        return self.clients.copy()
    
    def search_clients(self, query: str, active_only: bool = True) -> List[Dict]:
        """Search clients by name, email, or company"""
        query = query.lower()
        results = []
        
        for client in self.clients:
            if active_only and not client.get('is_active', True):
                continue
            
            searchable_fields = [
                client.get('name', ''),
                client.get('email', ''),
                client.get('company', ''),
                client.get('id', '')
            ]
            
            if any(query in field.lower() for field in searchable_fields):
                results.append(client.copy())
        
        return results
    
    def get_client_summary(self) -> Dict:
        """Get summary statistics about clients"""
        active_clients = [c for c in self.clients if c.get('is_active', True)]
        inactive_clients = [c for c in self.clients if not c.get('is_active', True)]
        
        return {
            'total_clients': len(self.clients),
            'active_clients': len(active_clients),
            'inactive_clients': len(inactive_clients),
            'countries': list(set(c.get('country', '') for c in active_clients if c.get('country'))),
            'currencies': list(set(c.get('currency', 'USD') for c in active_clients)),
        }
    
    def export_clients(self, format: str = 'json') -> str:
        """Export clients to different formats"""
        if format.lower() == 'json':
            return json.dumps(self.clients, indent=2, ensure_ascii=False)
        elif format.lower() == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            if self.clients:
                fieldnames = self.clients[0].keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.clients)
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def import_clients(self, data: str, format: str = 'json') -> int:
        """Import clients from different formats"""
        imported_count = 0
        
        if format.lower() == 'json':
            try:
                import_data = json.loads(data)
                for client_data in import_data:
                    # Remove ID to generate new ones
                    client_data.pop('id', None)
                    self.add_client(client_data)
                    imported_count += 1
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON data: {e}")
        elif format.lower() == 'csv':
            import csv
            import io
            
            reader = csv.DictReader(io.StringIO(data))
            for row in reader:
                # Remove empty strings and None values
                client_data = {k: v for k, v in row.items() if v}
                # Remove ID to generate new ones
                client_data.pop('id', None)
                self.add_client(client_data)
                imported_count += 1
        else:
            raise ValueError(f"Unsupported import format: {format}")
        
        return imported_count

def main():
    """CLI interface for client management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Client Management System")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add client command
    add_parser = subparsers.add_parser('add', help='Add a new client')
    add_parser.add_argument('--name', required=True, help='Client name')
    add_parser.add_argument('--email', required=True, help='Client email')
    add_parser.add_argument('--company', help='Company name')
    add_parser.add_argument('--phone', help='Phone number')
    add_parser.add_argument('--address', help='Street address')
    add_parser.add_argument('--city', help='City')
    add_parser.add_argument('--state', help='State/Province')
    add_parser.add_argument('--postal-code', help='Postal/ZIP code')
    add_parser.add_argument('--country', help='Country')
    add_parser.add_argument('--website', help='Website URL')
    add_parser.add_argument('--tax-id', help='Tax ID number')
    add_parser.add_argument('--payment-terms', default='Net 30', help='Payment terms')
    add_parser.add_argument('--currency', default='USD', help='Preferred currency')
    add_parser.add_argument('--notes', help='Additional notes')
    
    # List clients command
    list_parser = subparsers.add_parser('list', help='List all clients')
    list_parser.add_argument('--include-inactive', action='store_true', help='Include inactive clients')
    list_parser.add_argument('--format', choices=['table', 'json'], default='table', help='Output format')
    
    # Search clients command
    search_parser = subparsers.add_parser('search', help='Search clients')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--include-inactive', action='store_true', help='Include inactive clients')
    
    # Get client command
    get_parser = subparsers.add_parser('get', help='Get client details')
    get_parser.add_argument('client_id', help='Client ID')
    
    # Update client command
    update_parser = subparsers.add_parser('update', help='Update client information')
    update_parser.add_argument('client_id', help='Client ID')
    update_parser.add_argument('--name', help='Client name')
    update_parser.add_argument('--email', help='Client email')
    update_parser.add_argument('--company', help='Company name')
    update_parser.add_argument('--phone', help='Phone number')
    update_parser.add_argument('--address', help='Street address')
    update_parser.add_argument('--city', help='City')
    update_parser.add_argument('--state', help='State/Province')
    update_parser.add_argument('--postal-code', help='Postal/ZIP code')
    update_parser.add_argument('--country', help='Country')
    update_parser.add_argument('--website', help='Website URL')
    update_parser.add_argument('--tax-id', help='Tax ID number')
    update_parser.add_argument('--payment-terms', help='Payment terms')
    update_parser.add_argument('--currency', help='Preferred currency')
    update_parser.add_argument('--notes', help='Additional notes')
    
    # Delete client command
    delete_parser = subparsers.add_parser('delete', help='Delete (deactivate) a client')
    delete_parser.add_argument('client_id', help='Client ID')
    
    # Summary command
    subparsers.add_parser('summary', help='Show client summary statistics')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export clients')
    export_parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Export format')
    export_parser.add_argument('--output', help='Output file (default: stdout)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize client manager
    cm = ClientManager()
    
    try:
        if args.command == 'add':
            client_data = {
                'name': args.name,
                'email': args.email,
                'company': args.company or '',
                'phone': args.phone or '',
                'address': args.address or '',
                'city': args.city or '',
                'state': args.state or '',
                'postal_code': getattr(args, 'postal_code') or '',
                'country': args.country or '',
                'website': args.website or '',
                'tax_id': getattr(args, 'tax_id') or '',
                'payment_terms': getattr(args, 'payment_terms') or 'Net 30',
                'currency': args.currency or 'USD',
                'notes': args.notes or ''
            }
            
            client_id = cm.add_client(client_data)
            print(f"✅ Client added successfully with ID: {client_id}")
        
        elif args.command == 'list':
            clients = cm.list_clients(active_only=not args.include_inactive)
            
            if args.format == 'json':
                print(json.dumps(clients, indent=2))
            else:
                if not clients:
                    print("No clients found.")
                else:
                    print(f"{'ID':<10} {'Name':<25} {'Email':<30} {'Company':<20}")
                    print("-" * 85)
                    for client in clients:
                        print(f"{client['id']:<10} {client['name'][:24]:<25} {client['email'][:29]:<30} {client.get('company', '')[:19]:<20}")
        
        elif args.command == 'search':
            clients = cm.search_clients(args.query, active_only=not args.include_inactive)
            
            if not clients:
                print(f"No clients found matching '{args.query}'")
            else:
                print(f"Found {len(clients)} client(s) matching '{args.query}':")
                print(f"{'ID':<10} {'Name':<25} {'Email':<30} {'Company':<20}")
                print("-" * 85)
                for client in clients:
                    print(f"{client['id']:<10} {client['name'][:24]:<25} {client['email'][:29]:<30} {client.get('company', '')[:19]:<20}")
        
        elif args.command == 'get':
            client = cm.get_client(args.client_id)
            if client:
                print(json.dumps(client, indent=2))
            else:
                print(f"❌ Client not found: {args.client_id}")
        
        elif args.command == 'update':
            updates = {}
            for field in ['name', 'email', 'company', 'phone', 'address', 'city', 'state', 'country', 'website', 'notes']:
                value = getattr(args, field, None)
                if value is not None:
                    updates[field] = value
            
            # Handle fields with dashes in CLI
            if hasattr(args, 'postal_code') and args.postal_code is not None:
                updates['postal_code'] = args.postal_code
            if hasattr(args, 'tax_id') and args.tax_id is not None:
                updates['tax_id'] = args.tax_id
            if hasattr(args, 'payment_terms') and args.payment_terms is not None:
                updates['payment_terms'] = args.payment_terms
            if hasattr(args, 'currency') and args.currency is not None:
                updates['currency'] = args.currency
            
            if updates:
                if cm.update_client(args.client_id, updates):
                    print(f"✅ Client {args.client_id} updated successfully")
                else:
                    print(f"❌ Client not found: {args.client_id}")
            else:
                print("❌ No updates provided")
        
        elif args.command == 'delete':
            if cm.delete_client(args.client_id):
                print(f"✅ Client {args.client_id} deactivated successfully")
            else:
                print(f"❌ Client not found: {args.client_id}")
        
        elif args.command == 'summary':
            summary = cm.get_client_summary()
            print("📊 Client Summary:")
            print(f"Total Clients: {summary['total_clients']}")
            print(f"Active Clients: {summary['active_clients']}")
            print(f"Inactive Clients: {summary['inactive_clients']}")
            print(f"Countries: {', '.join(summary['countries']) if summary['countries'] else 'None'}")
            print(f"Currencies: {', '.join(summary['currencies'])}")
        
        elif args.command == 'export':
            export_data = cm.export_clients(args.format)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(export_data)
                print(f"✅ Clients exported to {args.output}")
            else:
                print(export_data)
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()