#!/bin/bash
# Tennis Court Monitor Setup Script

echo "🎾 Setting up Tennis Court Booking Automation..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.7+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
python -m playwright install --with-deps

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️ Creating .env configuration file..."
    cp env.example .env
    echo "📝 Please edit .env file with your Better/GLL credentials and settings"
else
    echo "⚙️ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Better/GLL login credentials"
echo "2. Test the monitor: source venv/bin/activate && python watcher.py"
echo "3. Set up cron job for automatic monitoring (see README.md)"
echo ""
echo "For help, see README.md or run: python watcher.py --help"
