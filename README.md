### InnoFeed – AI-Powered Patent & Research Feed Platform

A personalized, AI-driven feed that aggregates and summarizes the latest patents and research papers across selected technology domains, enabling users to stay updated without manual searching.

### About

InnoFeed is an intelligent web platform designed to deliver domain-specific feeds of newly published patents and research articles. The system integrates data from Lens.org (for patents) and arXiv (for research papers), processes them using NLP pipelines, and generates concise summaries tailored to the user’s preferences.

Traditional research discovery requires time-consuming searches across multiple platforms. InnoFeed resolves this by automating data ingestion, classification, summarization, and feed generation—ensuring researchers, students, and innovators receive timely and relevant insights with minimal effort.

### Features

AI-powered summarization using transformer-based NLP models

Automated patent and research ingestion from Lens.org & arXiv

Domain-based classification using custom NLP pipelines

Clean, personalized feed interface for each user

High scalability with asynchronous data fetching (HTTPX)

Secure authentication using Supabase Auth

Cloud-ready architecture with backend on Render and frontend on Vercel

PostgreSQL database on Supabase (free tier)

### Requirements
Operating System

Compatible with 64-bit systems such as Windows 10/11, Ubuntu, or macOS.

Development Environment

Python 3.10+ for backend development

Node.js 18+ if using React + Tailwind for the frontend

Backend Framework

FastAPI for scalable API development

HTTPX for async data ingestion

NLP & Machine Learning

HuggingFace Transformers

SentencePiece / Tokenizers

scikit-learn for domain classification

Database & Authentication

Supabase (PostgreSQL, Auth, Storage)

Frontend

Streamlit or React + Tailwind CSS

Additional Dependencies

Uvicorn

SQLModel / SQLAlchemy

python-dotenv

arXiv API

Lens.org API integration

Version Control

Git for collaboration and repository management

IDE

Suitable options: VSCode, PyCharm, WebStorm
### System Architecture
<img width="833" height="439" alt="image" src="https://github.com/user-attachments/assets/3f09e3d7-f854-4af9-8f9e-1f55a4e035a4" />


### Workflows
1. Data Ingestion Workflow
API Sources → Fetch New Records → Clean & Normalize → Store in DB

2. NLP Summarization & Classification Pipeline
Raw Text → Tokenization → Transformer Model → Summary Output
                          → Domain Classifier → Category Tag

3. User Feed Generation Workflow
User Login → Domain Selection → Query Latest Items → Display Feed → Read Summaries

### Output
<img width="785" height="469" alt="image" src="https://github.com/user-attachments/assets/bab67a48-c178-4d3f-b365-eaafc24b1958" />


### Results and Impact

InnoFeed improves research efficiency by automating repetitive search tasks.
It benefits:

Students

Researchers

Innovators

Patent analysts

The platform enhances discovery workflows and reduces cognitive load, contributing to faster innovation cycles.

