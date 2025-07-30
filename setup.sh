#!/bin/bash

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting DJAMMS deployment setup...${NC}"

# 1. Check system requirements
echo "Checking system requirements..."

# Check Python
python3 --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

# Check Node.js
node --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${RED}Node.js is not installed. Please install Node.js 16 or higher.${NC}"
    exit 1
fi

# Check FFmpeg
ffmpeg -version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${RED}FFmpeg is not installed. Please install FFmpeg.${NC}"
    exit 1
fi

# Check mpg123
mpg123 --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${RED}mpg123 is not installed. Please install mpg123.${NC}"
    exit 1
fi

# 2. Set up Python virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 3. Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# 4. Set up environment variables
echo "Setting up environment variables..."
if [ ! -f .env ]; then
    cat > .env << EOL
FLASK_APP=backend.main
FLASK_ENV=development
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(16))')
DATABASE_URL=postgresql://localhost/djamms
REDIS_URL=redis://localhost:6379/0
UPLOAD_FOLDER=uploads
EOL
fi

# 5. Create necessary directories
echo "Creating necessary directories..."
mkdir -p uploads
mkdir -p logs

# 6. Set up frontend
echo "Setting up frontend..."
cd base44.Handmade_Repo

# Install npm dependencies
npm install

# Create frontend environment file if it doesn't exist
if [ ! -f .env ]; then
    cat > .env << EOL
VITE_API_BASE_URL=http://localhost:5000
VITE_APP_NAME=DJAMMS
VITE_APP_VERSION=3.29.0
VITE_ENABLE_SPOTIFY=true
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_MONITORING=true
VITE_DEBUG_MODE=true
VITE_LOG_LEVEL=info
EOL
fi

# 7. Database setup
echo "Setting up database..."
flask db upgrade

echo -e "${GREEN}Setup complete!${NC}"
echo "
To start the application:

1. Start the backend:
   cd backend
   flask run --host=0.0.0.0 --port=5000

2. In a new terminal, start the frontend:
   cd base44.Handmade_Repo
   npm run dev

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
"
