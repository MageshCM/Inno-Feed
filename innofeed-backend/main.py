import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, Text, DateTime, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote
import bcrypt
from pydantic import BaseModel
from typing import List

# --- Database Configuration ---
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = quote(os.getenv("DB_PASSWORD", ""))
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    raise RuntimeError("Database environment variables are not fully set in .env file.")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Security and Hashing with Direct bcrypt ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        password_bytes = plain_password.encode('utf-8')[:72]
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception as e:
        print(f"Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

# --- Pydantic Models for API Validation ---
class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserPreferences(BaseModel):
    domain_ids: List[int]

# --- Database Models (SQLAlchemy) ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    name = Column(Text)

class Domain(Base):
    __tablename__ = "domains"
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    type = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    abstract = Column(Text)
    summary = Column(Text)
    authors = Column(Text)
    date = Column(DateTime)
    source = Column(Text)
    domain_id = Column(Integer, ForeignKey("domains.id"))
    
    # Patent-specific columns
    application_number = Column(Text)
    application_status = Column(Text)
    publication_date = Column(Text)
    uspc_classification = Column(Text)
    cpc_classifications = Column(Text)
    assignee = Column(Text)
    priority_date = Column(Text)
    patent_family_id = Column(Text)
    patent_pdf_url = Column(Text)
    thumbnail_url = Column(Text)
    cited_by_count = Column(Integer)
    
    # Paper-specific columns
    arxiv_id = Column(Text)
    pdf_url = Column(Text)
    doi = Column(Text)
    journal_ref = Column(Text)
    categories = Column(Text)
    comment = Column(Text)

class UserDomainPreference(Base):
    __tablename__ = "user_domain_preferences"
    __table_args__ = (PrimaryKeyConstraint('user_id', 'domain_id'),)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=False)

# Initialize the FastAPI app
app = FastAPI()

# --- CORS Middleware Configuration ---
origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---
@app.get("/")
def root():
    return {"message": "InnoFeed backend running"}

@app.post("/register")
def register_user(user_data: UserCreate):
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email, 
            password_hash=hashed_password,
            name=user_data.name
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "User registered successfully", "user_id": new_user.id}
    finally:
        db.close()

@app.post("/login")
def login_user(user_data: UserLogin):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == user_data.email).first()
        if not user or not verify_password(user_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        return {
            "message": "Login successful", 
            "user_id": user.id,
            "name": user.name or user.email.split('@')[0]  # Return name or email prefix
        }
    finally:
        db.close()

@app.post("/set-preferences/{user_id}")
def set_preferences(user_id: int, preferences: UserPreferences):
    db = SessionLocal()
    try:
        db.query(UserDomainPreference).filter(UserDomainPreference.user_id == user_id).delete()
        
        for domain_id in preferences.domain_ids:
            preference = UserDomainPreference(user_id=user_id, domain_id=domain_id)
            db.add(preference)
        
        db.commit()
        return {"message": "Preferences saved successfully"}
    finally:
        db.close()

@app.get("/domains")
def get_domains():
    db = SessionLocal()
    try:
        domains = db.query(Domain).all()
        return [{"id": d.id, "name": d.name} for d in domains]
    finally:
        db.close()

@app.get("/feed/{user_id}")
def get_feed(user_id: int):
    """Generates a personalized feed with ALL available fields"""
    db = SessionLocal()
    try:
        user_domains = db.query(UserDomainPreference.domain_id).filter(
            UserDomainPreference.user_id == user_id
        ).all()
        
        if not user_domains:
            return {
                "user_id": user_id, 
                "feed": [], 
                "message": "No domain preferences found for this user."
            }
        
        domain_ids = [d[0] for d in user_domains]
        
        items_query = db.query(Item).filter(
            Item.domain_id.in_(domain_ids)
        ).order_by(Item.date.desc()).all()
        
        feed = []
        for it in items_query:
            # Base fields common to both papers and patents
            feed_item = {
                "id": it.id,
                "type": it.type,
                "title": it.title,
                "abstract": it.abstract,
                "summary": it.summary,
                "authors": it.authors,
                "date": it.date.isoformat() if it.date else None,
                "source": it.source,
                "domain_id": it.domain_id,
            }
            
            # Add paper-specific fields
            if it.type == "paper":
                feed_item.update({
                    "arxiv_id": it.arxiv_id,
                    "pdf_url": it.pdf_url,
                    "doi": it.doi,
                    "journal_ref": it.journal_ref,
                    "categories": it.categories,
                    "comment": it.comment
                })
            
            # Add patent-specific fields
            elif it.type == "patent":
                feed_item.update({
                    "application_number": it.application_number,
                    "application_status": it.application_status,
                    "publication_date": it.publication_date,
                    "uspc_classification": it.uspc_classification,
                    "cpc_classifications": it.cpc_classifications,
                    "assignee": it.assignee,
                    "priority_date": it.priority_date,
                    "patent_family_id": it.patent_family_id,
                    "patent_pdf_url": it.patent_pdf_url,
                    "thumbnail_url": it.thumbnail_url,
                    "cited_by_count": it.cited_by_count
                })
            
            feed.append(feed_item)
        
        return {"user_id": user_id, "feed": feed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB query failed: {e}")
    finally:
        db.close()