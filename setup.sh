#!/bin/bash

# Invoice Generator Project Setup Script
# This script sets up the complete invoice generator system for team collaboration
# Works on macOS, Linux, and Windows (with Git Bash)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project configuration
PROJECT_NAME="Invoice Generator"
PYTHON_VERSION="3.8"
VENV_NAME="invoice_gen_env"
DJANGO_PROJECT="invoice_saas"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Function to install Python on different OS
install_python() {
    local os=$(detect_os)
    print_status "Installing Python $PYTHON_VERSION..."
    
    case $os in
        "linux")
            if command_exists apt-get; then
                sudo apt-get update
                sudo apt-get install -y python3 python3-pip python3-venv python3-dev
            elif command_exists yum; then
                sudo yum install -y python3 python3-pip python3-venv python3-devel
            elif command_exists pacman; then
                sudo pacman -S python python-pip
            else
                print_error "Unsupported Linux distribution. Please install Python manually."
                exit 1
            fi
            ;;
        "macos")
            if command_exists brew; then
                brew install python@3.10
            else
                print_error "Homebrew not found. Please install Python manually or install Homebrew first."
                print_status "To install Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                exit 1
            fi
            ;;
        "windows")
            print_error "Please install Python from https://python.org/downloads/ and ensure it's in your PATH"
            exit 1
            ;;
        *)
            print_error "Unsupported operating system. Please install Python manually."
            exit 1
            ;;
    esac
}

# Function to check Python installation
check_python() {
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_error "Python not found. Installing Python..."
        install_python
        return
    fi
    
    # Check Python version
    PYTHON_VERSION_ACTUAL=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_status "Found Python $PYTHON_VERSION_ACTUAL"
    
    if [[ $(echo "$PYTHON_VERSION_ACTUAL 3.7" | awk '{print ($1 >= $2)}') == 1 ]]; then
        print_success "Python version is compatible"
    else
        print_error "Python version $PYTHON_VERSION_ACTUAL is too old. Minimum required: 3.7"
        exit 1
    fi
}

# Function to check and install Git
check_git() {
    if ! command_exists git; then
        print_error "Git not found. Please install Git and try again."
        local os=$(detect_os)
        case $os in
            "linux")
                print_status "Install with: sudo apt-get install git (Ubuntu/Debian) or sudo yum install git (CentOS/RHEL)"
                ;;
            "macos")
                print_status "Install with: brew install git or download from https://git-scm.com/"
                ;;
            "windows")
                print_status "Download from: https://git-scm.com/download/win"
                ;;
        esac
        exit 1
    else
        print_success "Git found: $(git --version)"
    fi
}

# Function to create virtual environment
create_virtual_env() {
    print_status "Creating Python virtual environment: $VENV_NAME"
    
    if [ -d "$VENV_NAME" ]; then
        print_warning "Virtual environment already exists. Removing old environment..."
        rm -rf "$VENV_NAME"
    fi
    
    $PYTHON_CMD -m venv "$VENV_NAME"
    print_success "Virtual environment created successfully"
}

# Function to activate virtual environment
activate_virtual_env() {
    print_status "Activating virtual environment..."
    
    if [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        source "$VENV_NAME/Scripts/activate"
    else
        source "$VENV_NAME/bin/activate"
    fi
    
    print_success "Virtual environment activated"
}

# Function to upgrade pip
upgrade_pip() {
    print_status "Upgrading pip to latest version..."
    python -m pip install --upgrade pip
    print_success "Pip upgraded successfully"
}

# Function to install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies from requirements.txt..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found!"
        exit 1
    fi
    
    pip install -r requirements.txt
    print_success "Python dependencies installed successfully"
    
    # Install Django if not already in requirements
    if ! pip list | grep -i django > /dev/null; then
        print_status "Installing Django..."
        pip install django
    fi
    
    # Install additional development dependencies
    print_status "Installing additional development dependencies..."
    pip install django-debug-toolbar python-decouple
}

# Function to setup Django database
setup_database() {
    print_status "Setting up Django database..."
    
    if [ ! -f "manage.py" ]; then
        print_error "manage.py not found! Make sure you're in the project root directory."
        exit 1
    fi
    
    # Run Django migrations
    print_status "Running Django migrations..."
    python manage.py makemigrations
    python manage.py migrate
    
    print_success "Database setup completed"
}

# Function to create Django superuser
create_superuser() {
    print_status "Creating Django superuser (optional)..."
    echo "Would you like to create a Django admin superuser? (y/n)"
    read -r create_user
    
    if [[ $create_user == "y" || $create_user == "Y" ]]; then
        print_status "Creating superuser. Please follow the prompts:"
        python manage.py createsuperuser
        print_success "Superuser created successfully"
    else
        print_status "Skipping superuser creation. You can create one later with: python manage.py createsuperuser"
    fi
}

# Function to collect static files
collect_static() {
    print_status "Collecting Django static files..."
    python manage.py collectstatic --noinput
    print_success "Static files collected"
}

# Function to setup CLI configuration
setup_cli_config() {
    print_status "Setting up CLI configuration..."
    
    # Create data directory if it doesn't exist
    mkdir -p data
    
    # Create invoices directory if it doesn't exist
    mkdir -p invoices
    
    # Initialize CLI configuration if it doesn't exist
    if [ ! -f "config.json" ]; then
        print_status "No CLI configuration found. You can set it up later by running:"
        print_status "python invoice_generator.py setup"
    fi
    
    print_success "CLI directories created"
}

# Function to run tests
run_tests() {
    print_status "Running project tests..."
    
    # Run Django tests
    if [ -f "manage.py" ]; then
        print_status "Running Django tests..."
        python manage.py test
    fi
    
    # Test CLI functionality
    if [ -f "invoice_generator.py" ]; then
        print_status "Testing CLI functionality..."
        python invoice_generator.py --help > /dev/null
        print_success "CLI is working correctly"
    fi
}

# Function to create environment file
create_env_file() {
    print_status "Creating environment configuration file..."
    
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# Django Configuration
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration (SQLite by default)
DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration (optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Invoice Configuration
DEFAULT_TAX_RATE=0.0
INVOICE_NUMBER_PREFIX=INV-
EOF
        print_success "Environment file created (.env)"
        print_warning "Please update the SECRET_KEY in .env file for production use"
    else
        print_status ".env file already exists"
    fi
}

# Function to display final instructions
display_instructions() {
    print_success "=========================================="
    print_success "🎉 $PROJECT_NAME Setup Complete!"
    print_success "=========================================="
    echo ""
    print_status "Next steps:"
    echo "1. Activate virtual environment:"
    echo "   source $VENV_NAME/bin/activate  (Linux/macOS)"
    echo "   source $VENV_NAME/Scripts/activate  (Windows)"
    echo ""
    print_status "2. Start Django development server:"
    echo "   python manage.py runserver"
    echo "   Then visit: http://127.0.0.1:8000"
    echo ""
    print_status "3. Use CLI invoice generator:"
    echo "   python invoice_generator.py setup    # Configure business info"
    echo "   python invoice_generator.py add-client    # Add clients"
    echo "   python invoice_generator.py create-invoice    # Create invoices"
    echo "   python invoice_generator.py list-clients    # List all clients"
    echo ""
    print_status "4. Access Django admin (if superuser created):"
    echo "   http://127.0.0.1:8000/admin/"
    echo ""
    print_status "Project structure:"
    echo "   📁 Django Web App: Complete invoice management system"
    echo "   📁 CLI Tool: Command-line invoice generator"
    echo "   📁 data/: Client data storage"
    echo "   📁 invoices/: Generated PDF invoices"
    echo "   📁 static/: Web app static files"
    echo "   📁 templates/: Django templates"
    echo ""
    print_warning "Important files:"
    echo "   📄 requirements.txt: Python dependencies"
    echo "   📄 manage.py: Django management commands"
    echo "   📄 invoice_generator.py: CLI invoice tool"
    echo "   📄 .env: Environment configuration"
    echo ""
    print_success "Happy invoicing! 🧾"
}

# Main setup function
main() {
    print_status "Starting $PROJECT_NAME setup..."
    print_status "=========================================="
    
    # Check if we're in the right directory
    if [ ! -f "requirements.txt" ] || [ ! -f "manage.py" ]; then
        print_error "Please run this script from the project root directory"
        print_error "Make sure requirements.txt and manage.py are present"
        exit 1
    fi
    
    # Pre-flight checks
    check_git
    check_python
    
    # Setup virtual environment
    create_virtual_env
    activate_virtual_env
    upgrade_pip
    
    # Install dependencies
    install_dependencies
    
    # Setup Django
    create_env_file
    setup_database
    collect_static
    
    # Setup CLI
    setup_cli_config
    
    # Optional superuser creation
    create_superuser
    
    # Run tests
    print_status "Would you like to run tests to verify setup? (y/n)"
    read -r run_test
    if [[ $run_test == "y" || $run_test == "Y" ]]; then
        run_tests
    fi
    
    # Display final instructions
    display_instructions
}

# Check if script is being run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi