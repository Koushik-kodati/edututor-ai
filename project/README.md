# EduTutor AI - Personalized Learning Platform

A comprehensive AI-powered educational platform that provides personalized quiz generation, student assessment, and learning analytics using IBM Granite foundation models.

## 🌟 Features

### For Students
- **AI-Generated Quizzes**: Personalized quizzes created by IBM Granite models
- **Adaptive Learning**: Difficulty adjusts based on performance
- **Real-time Feedback**: Instant results and explanations
- **Progress Tracking**: Comprehensive learning analytics
- **Google Classroom Integration**: Seamless course synchronization

### For Educators
- **Student Dashboard**: Monitor all student progress in real-time
- **Performance Analytics**: Detailed insights and reports
- **Course Management**: Integrate with Google Classroom
- **Custom Quiz Creation**: Generate targeted assessments

## 🏗️ Architecture

```
Frontend (React/TypeScript)
├── Student Dashboard
├── Educator Dashboard
├── Quiz Interface
└── Authentication

Backend (FastAPI/Python)
├── IBM Watsonx + Granite Models
├── Pinecone Vector Database
├── Google Classroom API
└── RESTful API Endpoints

AI/ML Components
├── IBM Granite 3.3-2B Instruct Model
├── LangChain Integration
├── Vector Embeddings
└── Adaptive Learning Algorithms
```

## 🚀 Quick Start

### Option 1: Google Colab (Recommended)

1. **Upload to Colab**:
   ```bash
   # Upload the entire project folder to Google Colab
   ```

2. **Run Setup**:
   ```python
   !python colab_setup.py
   ```

3. **Start Backend**:
   ```python
   !python colab_backend.py
   ```

4. **Launch Frontend**:
   ```python
   !streamlit run streamlit_app.py
   ```

### Option 2: Local Development

1. **Clone Repository**:
   ```bash
   git clone <repository-url>
   cd edututor-ai
   ```

2. **Install Dependencies**:
   ```bash
   # Frontend
   npm install

   # Backend
   cd backend
   pip install -r requirements.txt
   ```

3. **Environment Setup**:
   ```bash
   cp backend/.env.example backend/.env
   # Edit .env with your credentials
   ```

4. **Start Services**:
   ```bash
   # Backend
   cd backend
   python main.py

   # Frontend
   npm run dev
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# IBM Watsonx Configuration
WATSONX_MODEL_ID=ibm-granite/granite-3.3-2b-instruct
WATSONX_API_KEY=your_ibm_watsonx_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_ENDPOINT=https://us-south.ml.cloud.ibm.com

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=edututorai

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

### IBM Watsonx Setup

1. Create an IBM Cloud account
2. Set up Watsonx.ai service
3. Get your API key and project ID
4. Configure the Granite model access

### Pinecone Setup

1. Create a Pinecone account
2. Create a new index named "edututorai"
3. Get your API key
4. Configure the index settings

### Google Classroom Setup

1. Create a Google Cloud Project
2. Enable Classroom API
3. Set up OAuth 2.0 credentials
4. Configure redirect URIs

## 📱 Usage

### Student Workflow

1. **Login**: Use email/password or Google OAuth
2. **Select Topic**: Choose from available subjects
3. **Set Difficulty**: Easy, Medium, or Hard
4. **Take Quiz**: Answer AI-generated questions
5. **View Results**: Get instant feedback and explanations
6. **Track Progress**: Monitor learning analytics

### Educator Workflow

1. **Login**: Access educator dashboard
2. **View Students**: Monitor all student progress
3. **Analyze Performance**: Review detailed analytics
4. **Sync Classrooms**: Import from Google Classroom
5. **Generate Reports**: Export performance data

## 🧠 AI Integration

### IBM Granite Model

The platform uses IBM's Granite 3.3-2B Instruct model for:
- Dynamic quiz question generation
- Contextual explanations
- Adaptive difficulty adjustment
- Personalized learning paths

### Vector Database

Pinecone stores:
- User learning profiles
- Quiz performance embeddings
- Similarity-based recommendations
- Adaptive learning patterns

## 🔒 Security

- OAuth 2.0 authentication
- JWT token management
- API rate limiting
- Data encryption
- Privacy compliance

## 📊 Analytics

### Student Metrics
- Quiz scores and trends
- Time spent learning
- Topic mastery levels
- Learning streaks

### Educator Insights
- Class performance overview
- Individual student progress
- Topic difficulty analysis
- Engagement metrics

## 🛠️ Development

### Frontend Stack
- React 18 with TypeScript
- Tailwind CSS for styling
- Framer Motion for animations
- React Router for navigation
- Axios for API calls

### Backend Stack
- FastAPI with Python 3.9+
- Pydantic for data validation
- SQLAlchemy for database ORM
- JWT for authentication
- Uvicorn ASGI server

### AI/ML Stack
- IBM Watsonx.ai
- LangChain framework
- Pinecone vector database
- Hugging Face transformers
- PyTorch for model inference

## 📈 Roadmap

- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Voice-based quizzes
- [ ] Collaborative learning features
- [ ] Integration with more LMS platforms

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation

## 🙏 Acknowledgments

- IBM for Watsonx.ai and Granite models
- Google for Classroom API
- Pinecone for vector database
- The open-source community

---

**EduTutor AI** - Transforming education through personalized AI-powered learning experiences.