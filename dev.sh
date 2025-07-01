#!/bin/bash

# NetApp ActiveIQ API Documentation - Development Script
# This script provides convenient commands for local development

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_usage() {
    echo -e "${BLUE}NetApp ActiveIQ API Documentation - Development Script${NC}"
    echo ""
    echo "Usage: ./dev.sh [command]"
    echo ""
    echo "Commands:"
    echo "  setup       - Set up development environment"
    echo "  serve       - Start development server"
    echo "  build       - Build documentation"
    echo "  clean       - Clean build artifacts"
    echo "  validate    - Validate documentation"
    echo "  deploy      - Deploy to GitHub Pages"
    echo "  help        - Show this help message"
    echo ""
}

setup_env() {
    echo -e "${BLUE}Setting up development environment...${NC}"

    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: Python 3 is not installed${NC}"
        exit 1
    fi

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        python3 -m venv venv
    fi

    # Activate virtual environment
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate

    # Upgrade pip
    echo -e "${YELLOW}Upgrading pip...${NC}"
    pip install --upgrade pip

    # Install requirements
    echo -e "${YELLOW}Installing requirements...${NC}"
    pip install -r requirements.txt

    echo -e "${GREEN}✓ Development environment setup complete!${NC}"
    echo -e "${BLUE}To activate the environment manually, run: source venv/bin/activate${NC}"
}

serve_docs() {
    echo -e "${BLUE}Starting development server...${NC}"

    # Activate virtual environment
    source venv/bin/activate

    # Start MkDocs server
    echo -e "${YELLOW}Server will be available at: http://localhost:8000${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
    mkdocs serve --livereload
}

build_docs() {
    echo -e "${BLUE}Building documentation...${NC}"

    # Activate virtual environment
    source venv/bin/activate

    # Build documentation
    mkdocs build --clean --strict

    echo -e "${GREEN}✓ Documentation built successfully!${NC}"
    echo -e "${BLUE}Site generated in: ./site/${NC}"
}

clean_build() {
    echo -e "${BLUE}Cleaning build artifacts...${NC}"

    # Remove site directory
    if [ -d "site" ]; then
        rm -rf site
        echo -e "${GREEN}✓ Removed site directory${NC}"
    fi

    # Remove __pycache__ directories
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    echo -e "${GREEN}✓ Removed Python cache files${NC}"

    echo -e "${GREEN}✓ Clean complete!${NC}"
}

validate_docs() {
    echo -e "${BLUE}Validating documentation...${NC}"

    # Activate virtual environment
    source venv/bin/activate

    # Build with strict mode
    echo -e "${YELLOW}Building with strict mode...${NC}"
    mkdocs build --clean --strict

    # Check for common issues
    echo -e "${YELLOW}Checking for common issues...${NC}"

    # Check for broken internal links
    echo -e "${YELLOW}Checking internal links...${NC}"
    find docs/ -name "*.md" -exec grep -l "](\./" {} \; | while read file; do
        echo "Checking links in: $file"
        grep -n "](\./" "$file" | while read line; do
            link=$(echo "$line" | sed 's/.*](\.\///' | sed 's/).*//')
            if [ ! -f "docs/$link" ]; then
                echo -e "${RED}Broken link in $file: $link${NC}"
            fi
        done
    done

    # Check for required files
    required_files=("docs/index.md" "docs/api-endpoints.md" "docs/data-models.md" "docs/examples.md" "docs/advanced-use-cases.md")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            echo -e "${RED}Missing required file: $file${NC}"
        else
            echo -e "${GREEN}✓ Found: $file${NC}"
        fi
    done

    echo -e "${GREEN}✓ Validation complete!${NC}"
}

deploy_docs() {
    echo -e "${BLUE}Deploying to GitHub Pages...${NC}"

    # Activate virtual environment
    source venv/bin/activate

    # Build and deploy
    echo -e "${YELLOW}Building and deploying...${NC}"
    mkdocs gh-deploy --force

    echo -e "${GREEN}✓ Deployment complete!${NC}"
    echo -e "${BLUE}Documentation will be available at your GitHub Pages URL${NC}"
}

# Main script logic
case "$1" in
    setup)
        setup_env
        ;;
    serve)
        serve_docs
        ;;
    build)
        build_docs
        ;;
    clean)
        clean_build
        ;;
    validate)
        validate_docs
        ;;
    deploy)
        deploy_docs
        ;;
    help|--help|-h)
        print_usage
        ;;
    "")
        print_usage
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        print_usage
        exit 1
        ;;
esac
