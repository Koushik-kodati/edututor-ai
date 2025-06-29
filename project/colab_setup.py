"""
Google Colab Setup Script for EduTutor AI
Run this in Google Colab to set up the environment and download the IBM Granite model
"""

import os
import subprocess
import sys
import json

def install_requirements():
    """Install required packages"""
    print("🚀 Installing required packages...")
    
    requirements = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0", 
        "pydantic==2.5.0",
        "python-dotenv==1.0.0",
        "langchain-ibm==0.1.0",
        "pinecone-client==2.2.4",
        "streamlit==1.28.0",
        "requests==2.31.0",
        "python-multipart==0.0.6",
        "google-auth-oauthlib==1.1.0",
        "google-api-python-client==2.108.0",
        "plotly==5.17.0",
        "pandas==2.1.0",
        "gradio==4.8.0"
    ]
    
    for package in requirements:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("✅ All packages installed successfully!")

def setup_environment():
    """Set up environment variables"""
    print("🔧 Setting up environment...")
    
    env_content = """# IBM Watsonx Configuration
WATSONX_MODEL_ID=ibm-granite/granite-3.3-2b-instruct
WATSONX_API_KEY=0039ef2d-7d5c-484b-b755-b9e9ef1def3b
WATSONX_PROJECT_ID=745ffd81-1b96-4b26-9b8b-8b3332a07a1b
WATSONX_ENDPOINT=https://us-south.ml.cloud.ibm.com

# Pinecone Configuration
PINECONE_API_KEY=pcsk_75XQe3_7HhRdTkdpJHwbQy4diBDwN2ft2fRgkZvSPXq11ViLKDiLQb5yu8L3tjBw4Q99XG
PINECONE_INDEX_NAME=edututorai

# Google OAuth Configuration
GOOGLE_CLIENT_ID=1520821499-euf65nnfudmul7br4famp04mb5629ah9.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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

# Application Configuration
SECRET_KEY=your_secret_key_here
DEBUG=True
"""
    
    with open('backend/.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Environment file created!")

def create_directory_structure():
    """Create necessary directories"""
    print("📁 Creating directory structure...")
    
    directories = [
        "backend",
        "backend/services",
        "frontend",
        "models",
        "data"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Directory structure created!")

def create_colab_notebook():
    """Create a Jupyter notebook for easy Colab setup"""
    notebook_content = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# EduTutor AI - Google Colab Setup\\n",
                    "\\n",
                    "This notebook sets up the complete EduTutor AI application in Google Colab with IBM Granite model integration.\\n",
                    "\\n",
                    "## Features\\n",
                    "- IBM Watsonx + Granite 3.3-2B model integration\\n",
                    "- Pinecone vector database for adaptive learning\\n",
                    "- Google Classroom synchronization\\n",
                    "- FastAPI backend with comprehensive APIs\\n",
                    "- Streamlit frontend with role-based dashboards\\n",
                    "- Diagnostic testing and personalized recommendations"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Install and setup EduTutor AI\\n",
                    "!python colab_setup.py"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Start the FastAPI backend\\n",
                    "import subprocess\\n",
                    "import threading\\n",
                    "import time\\n",
                    "\\n",
                    "def start_backend():\\n",
                    "    subprocess.run(['python', 'backend/main.py'])\\n",
                    "\\n",
                    "# Start backend in background\\n",
                    "backend_thread = threading.Thread(target=start_backend)\\n",
                    "backend_thread.daemon = True\\n",
                    "backend_thread.start()\\n",
                    "\\n",
                    "print('🚀 Backend starting on http://localhost:8000')\\n",
                    "time.sleep(5)\\n",
                    "print('✅ Backend should be running now!')"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Test backend connection\\n",
                    "import requests\\n",
                    "\\n",
                    "try:\\n",
                    "    response = requests.get('http://localhost:8000/')\\n",
                    "    print('✅ Backend is running!')\\n",
                    "    print(f'Response: {response.json()}')\\n",
                    "except Exception as e:\\n",
                    "    print(f'❌ Backend connection failed: {e}')"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Start Streamlit frontend\\n",
                    "!streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 &"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Usage Instructions\\n",
                    "\\n",
                    "1. **Backend API**: Available at `http://localhost:8000`\\n",
                    "   - API Documentation: `http://localhost:8000/docs`\\n",
                    "   - Health Check: `http://localhost:8000/`\\n",
                    "\\n",
                    "2. **Streamlit Frontend**: Available at `http://localhost:8501`\\n",
                    "   - Student Dashboard\\n",
                    "   - Educator Dashboard\\n",
                    "   - Quiz Interface\\n",
                    "   - Analytics and Progress Tracking\\n",
                    "\\n",
                    "3. **Demo Credentials**:\\n",
                    "   - Student: `student@demo.com` / `password`\\n",
                    "   - Educator: `teacher@demo.com` / `password`\\n",
                    "\\n",
                    "## Key Features\\n",
                    "\\n",
                    "### For Students\\n",
                    "- Personalized quiz generation using IBM Granite AI\\n",
                    "- Adaptive difficulty based on performance\\n",
                    "- Diagnostic testing for skill assessment\\n",
                    "- Progress tracking and analytics\\n",
                    "- Learning recommendations\\n",
                    "\\n",
                    "### For Educators\\n",
                    "- Student progress monitoring\\n",
                    "- Class performance analytics\\n",
                    "- Google Classroom integration\\n",
                    "- Detailed reporting and insights"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    with open('EduTutor_AI_Colab.ipynb', 'w') as f:
        json.dump(notebook_content, f, indent=2)
    
    print("✅ Colab notebook created!")

def create_startup_script():
    """Create startup script for easy deployment"""
    startup_script = '''#!/bin/bash

echo "🚀 Starting EduTutor AI Platform..."

# Start backend
echo "Starting FastAPI backend..."
cd backend
python main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start frontend
echo "Starting Streamlit frontend..."
cd ..
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 &
FRONTEND_PID=$!

echo "✅ EduTutor AI is running!"
echo "📊 Frontend: http://localhost:8501"
echo "🔧 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"

# Keep script running
wait $BACKEND_PID $FRONTEND_PID
'''
    
    with open('start_edututor.sh', 'w') as f:
        f.write(startup_script)
    
    # Make executable
    os.chmod('start_edututor.sh', 0o755)
    
    print("✅ Startup script created!")

def main():
    """Main setup function"""
    print("🎓 Setting up EduTutor AI for Google Colab...")
    print("=" * 60)
    
    # Run setup steps
    create_directory_structure()
    print()
    
    install_requirements()
    print()
    
    setup_environment()
    print()
    
    create_colab_notebook()
    print()
    
    create_startup_script()
    print()
    
    print("=" * 60)
    print("✅ EduTutor AI setup complete!")
    print()
    print("📋 Next steps:")
    print("1. Upload this folder to Google Colab")
    print("2. Open EduTutor_AI_Colab.ipynb")
    print("3. Run the cells to start the application")
    print()
    print("🌐 The app will be available at:")
    print("- Streamlit Frontend: http://localhost:8501")
    print("- FastAPI Backend: http://localhost:8000")
    print("- API Documentation: http://localhost:8000/docs")
    print()
    print("🔑 Demo Credentials:")
    print("- Student: student@demo.com / password")
    print("- Educator: teacher@demo.com / password")

if __name__ == "__main__":
    main()