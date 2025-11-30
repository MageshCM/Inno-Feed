
InnoFeed - AI-Powered Research Feed
An intelligent research paper and patent discovery platform that delivers personalized feeds based on user interests.
🚀 Features

Personalized Feed: Get papers and patents based on your selected domains
Multi-Source Integration:

arXiv papers with full metadata
Google Patents with detailed classifications


Rich Details:

PDF downloads
Citation counts
Patent thumbnails
DOI links


User Authentication: Secure login and registration
Domain Preferences: AI, Robotics, Quantum Computing, Genetics, Cybersecurity, Blockchain

🛠️ Tech Stack
Backend

FastAPI: High-performance Python web framework
PostgreSQL: Relational database
SQLAlchemy: ORM for database operations
bcrypt: Password hashing
HuggingFace API: Text summarization

Frontend

React: UI library
Vite: Build tool
CSS: Custom styling

📋 Prerequisites

Python 3.8+
Node.js 16+
PostgreSQL database
HuggingFace API key (for summarization)
SerpAPI key (for patent fetching)

⚙️ Installation
1. Clone the repository
bashgit clone https://github.com/yourusername/innofeed.git
cd innofeed
2. Backend Setup
bashcd innofeed-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your configuration
# DB_USER=your_db_user
# DB_PASSWORD=your_db_password
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=innofeed
# HF_API_KEY=your_huggingface_key
# SERPAPI_KEY=your_serpapi_key

# Run data ingestion (first time)
python ingest.py

# Start backend server
uvicorn main:app --reload
3. Frontend Setup
bashcd innofeed-frontend

# Install dependencies
npm install

# Create .env file
# VITE_API_URL=http://localhost:8000

# Start development server
npm run dev
🗄️ Database Schema
Tables

users: User authentication
domains: Research domains
items: Papers and patents
user_domain_preferences: User interests

📚 API Endpoints

POST /register - Register new user
POST /login - User login
GET /domains - Get all domains
POST /set-preferences/{user_id} - Update user preferences
GET /feed/{user_id} - Get personalized feed

🔄 Data Ingestion
Run the ingestion script to fetch latest papers and patents:
bashpython ingest.py
🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
📝 License
This project is licensed under the MIT License.
👨‍💻 Author
Your Name - GitHub Profile
🙏 Acknowledgments

arXiv for research papers
Google Patents for patent data
HuggingFace for NLP models
