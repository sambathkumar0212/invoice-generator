# Team Setup Guide - Invoice Generator

This guide helps team members quickly set up the Invoice Generator project on their local machines.

## Quick Setup (Recommended)

### 1. Clone the Repository
```bash
git clone https://github.com/sambathkumar0212/invoice-generator.git
cd invoice-generator
```

### 2. Run the Setup Script
```bash
# Make the script executable (if needed)
chmod +x setup.sh

# Run the setup script
./setup.sh
```

The setup script will automatically:
- ✅ Check system requirements (Python, Git)
- ✅ Create virtual environment
- ✅ Install all Python dependencies
- ✅ Set up Django database
- ✅ Create environment configuration
- ✅ Set up CLI directories
- ✅ Run tests (optional)

## Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Prerequisites
- Python 3.7+ 
- Git
- pip (Python package manager)

### 2. Clone and Navigate
```bash
git clone https://github.com/sambathkumar0212/invoice-generator.git
cd invoice-generator
```

### 3. Create Virtual Environment
```bash
python3 -m venv invoice_gen_env
source invoice_gen_env/bin/activate  # Linux/macOS
# OR
invoice_gen_env\Scripts\activate     # Windows
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install django django-debug-toolbar python-decouple
```

### 5. Set Up Django
```bash
# Create environment file
cp .env.example .env  # Edit as needed

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser (optional)
python manage.py createsuperuser
```

### 6. Create CLI Directories
```bash
mkdir -p data invoices
```

## Running the Project

### Django Web Application
```bash
# Activate virtual environment
source invoice_gen_env/bin/activate

# Start development server
python manage.py runserver

# Visit: http://127.0.0.1:8000
```

### CLI Invoice Generator
```bash
# Setup business information (first time)
python invoice_generator.py setup

# Add clients
python invoice_generator.py add-client

# Create invoices
python invoice_generator.py create-invoice

# List clients
python invoice_generator.py list-clients
```

## Project Structure

```
invoice-generator/
├── 🔧 setup.sh                    # Automated setup script
├── 📋 requirements.txt             # Python dependencies
├── ⚙️ manage.py                    # Django management
├── 🧾 invoice_generator.py         # CLI invoice tool
├── 📁 invoice_saas/                # Django project
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── 📁 authentication/              # User authentication
├── 📁 companies/                   # Company management
├── 📁 invoice_management/          # Invoice management
├── 📁 templates/                   # HTML templates
├── 📁 static/                      # CSS, JS, images
├── 📁 data/                        # CLI client data
└── 📁 invoices/                    # Generated PDFs
```

## Common Development Tasks

### Running Tests
```bash
python manage.py test
```

### Database Operations
```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (if needed)
rm db.sqlite3
python manage.py migrate
```

### Managing Dependencies
```bash
# Add new dependency
pip install package_name
pip freeze > requirements.txt

# Update requirements
pip install -r requirements.txt --upgrade
```

## Environment Configuration

Create a `.env` file with these settings:

```env
# Django Configuration
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite by default)
DATABASE_URL=sqlite:///db.sqlite3

# Email (development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Invoice Settings
DEFAULT_TAX_RATE=0.0
INVOICE_NUMBER_PREFIX=INV-
```

## Troubleshooting

### Common Issues

1. **Python version error**
   ```bash
   # Check Python version
   python --version
   # Should be 3.7 or higher
   ```

2. **Virtual environment activation fails**
   ```bash
   # Linux/macOS
   source invoice_gen_env/bin/activate
   
   # Windows
   invoice_gen_env\Scripts\activate
   ```

3. **Database migration errors**
   ```bash
   # Reset migrations
   rm -rf */migrations/__pycache__
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Static files not loading**
   ```bash
   python manage.py collectstatic --noinput
   ```

5. **Permission denied on setup.sh**
   ```bash
   chmod +x setup.sh
   ```

### Getting Help

- Check the main README.md for detailed project information
- Review Django logs for web app issues
- Check CLI help: `python invoice_generator.py --help`
- For team questions, create an issue in the GitHub repository

## Contributing

1. Create a feature branch: `git checkout -b feature-name`
2. Make changes and test thoroughly
3. Commit: `git commit -m "Add feature description"`
4. Push: `git push origin feature-name`
5. Create pull request

## Team Resources

- **Repository**: https://github.com/sambathkumar0212/invoice-generator
- **Live Demo**: http://127.0.0.1:8000 (after running locally)
- **Django Admin**: http://127.0.0.1:8000/admin/

---

💡 **Tip**: Always activate your virtual environment before working on the project!

🚀 **Quick Start**: Just run `./setup.sh` and follow the prompts!