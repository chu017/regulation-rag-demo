#!/bin/bash
# Example setup script (for reference - Windows users should use PowerShell or run commands manually)

echo "Setting up Regulation RAG MVP..."

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env and add your GEMINI_API_KEY"
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your GEMINI_API_KEY to .env"
echo "2. Place PDF files in data/raw/{city}/"
echo "3. Run: python scripts/parse_pdf.py"
echo "4. Run: python scripts/chunk_text.py"
echo "5. Run: python scripts/embed_index.py"
echo "6. Run: streamlit run app/app.py"
