import os
from dotenv import load_dotenv
load_dotenv()

import requests
from sqlalchemy import create_engine, Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from urllib.parse import quote
import xml.etree.ElementTree as ET
import time
from nlp_utils import summarize_text, categorize_text

# --- Database Configuration ---
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = quote(os.getenv("DB_PASSWORD", ""))
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    raise RuntimeError("Database environment variables are not fully set in .env file.")

if not SERPAPI_KEY:
    print("Warning: SERPAPI_KEY not found. Patent fetching will be skipped.")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Database Models ---
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
    
    # Patent columns
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
    
    # Paper columns
    arxiv_id = Column(Text)
    pdf_url = Column(Text)
    doi = Column(Text)
    journal_ref = Column(Text)
    categories = Column(Text)
    comment = Column(Text)

# --- Data Ingestion Functions ---
def fetch_arxiv(domains_list, max_results=50):
    """Fetches recent papers from arXiv with enhanced metadata."""
    category_map = {
        "AI": "cs.AI",
        "Robotics": "cs.RO",
        "Quantum Computing": "quant-ph",
        "Genetics": "q-bio.GN",
        "Cybersecurity": "cs.CR",
        "Blockchain": "cs.CR"
    }

    all_papers = []

    for domain in domains_list:
        cat = category_map.get(domain)
        if not cat:
            continue

        url_base = f"http://export.arxiv.org/api/query?search_query=cat:{cat}&sortBy=submittedDate&sortOrder=descending"
        papers = []
        start = 0
        batch_size = 25

        while len(papers) < max_results:
            remaining = max_results - len(papers)
            fetch_size = min(batch_size, remaining)
            url = f"{url_base}&start={start}&max_results={fetch_size}"
            resp = requests.get(url)
            if resp.status_code != 200:
                print(f"Error fetching from arXiv ({domain}): {resp.status_code}")
                break

            root = ET.fromstring(resp.content)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            entries = root.findall("atom:entry", ns)
            if not entries:
                break

            for entry in entries:
                # Basic fields
                title = entry.find("atom:title", ns).text.strip() if entry.find("atom:title", ns) is not None else "No title"
                abstract = entry.find("atom:summary", ns).text.strip() if entry.find("atom:summary", ns) is not None else ""
                
                # Authors
                authors = ", ".join([
                    a.find("atom:name", ns).text
                    for a in entry.findall("atom:author", ns)
                    if a.find("atom:name", ns) is not None
                ])
                
                # Date
                published_str = entry.find("atom:published", ns).text if entry.find("atom:published", ns) is not None else None
                published = datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%SZ") if published_str else datetime.now()
                
                # NEW: Extract arXiv ID from entry ID
                entry_id_elem = entry.find("atom:id", ns)
                arxiv_id = entry_id_elem.text.split("/abs/")[-1] if entry_id_elem is not None else None
                
                # NEW: Extract PDF URL
                pdf_url = None
                for link in entry.findall("atom:link", ns):
                    if link.get("title") == "pdf":
                        pdf_url = link.get("href")
                        break
                
                # NEW: Extract DOI
                doi = None
                doi_elem = entry.find("atom:doi", ns)
                if doi_elem is not None:
                    doi = doi_elem.text
                
                # NEW: Extract categories
                categories = ", ".join([
                    cat.get("term")
                    for cat in entry.findall("atom:category", ns)
                    if cat.get("term") is not None
                ])
                
                # NEW: Extract journal reference
                journal_ref = None
                journal_elem = entry.find("atom:journal_ref", ns)
                if journal_elem is not None:
                    journal_ref = journal_elem.text
                
                # NEW: Extract comment
                comment = None
                comment_elem = entry.find("atom:comment", ns)
                if comment_elem is not None:
                    comment = comment_elem.text

                ai_summary = summarize_text(abstract)

                papers.append({
                    "type": "paper",
                    "title": title,
                    "abstract": abstract,
                    "summary": ai_summary,
                    "authors": authors,
                    "date": published,
                    "source": "arXiv",
                    "domain": domain,
                    # NEW fields
                    "arxiv_id": arxiv_id,
                    "pdf_url": pdf_url,
                    "doi": doi,
                    "categories": categories,
                    "journal_ref": journal_ref,
                    "comment": comment
                })
            
            start += fetch_size
            time.sleep(1)

        print(f"Fetched {len(papers)} papers for domain: {domain}")
        all_papers.extend(papers)

    return all_papers


def fetch_google_patents(domains_list, max_results=50):
    """Fetches patents from Google Patents with enhanced metadata."""
    if not SERPAPI_KEY:
        print("SERPAPI_KEY not set. Skipping patent fetching.")
        return []

    query_map = {
        "AI": "artificial intelligence OR machine learning",
        "Robotics": "robotics OR autonomous systems",
        "Quantum Computing": "quantum computing OR quantum information",
        "Genetics": "genetics OR genomics OR DNA",
        "Cybersecurity": "cybersecurity OR network security OR encryption",
        "Blockchain": "blockchain OR distributed ledger OR cryptocurrency"
    }

    all_patents = []
    base_url = "https://serpapi.com/search"

    for domain in domains_list:
        query = query_map.get(domain)
        if not query:
            print(f"No query mapping for domain: {domain}. Skipping.")
            continue

        patents = []
        page = 0
        results_per_page = 20
        
        while len(patents) < max_results:
            params = {
                "engine": "google_patents",
                "q": query,
                "api_key": SERPAPI_KEY,
                "start": page * results_per_page,
                "num": results_per_page
            }

            try:
                response = requests.get(base_url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()

                organic_results = data.get("organic_results", [])
                
                if not organic_results:
                    print(f"No more results for domain: {domain}")
                    break

                for result in organic_results:
                    if len(patents) >= max_results:
                        break

                    # Basic fields
                    title = result.get("title", "No title")
                    snippet = result.get("snippet", "")
                    patent_id = result.get("patent_id", "N/A")
                    
                    # Publication date
                    pub_date_str = result.get("publication_date", "")
                    try:
                        pub_date = datetime.strptime(pub_date_str, "%Y-%m-%d") if pub_date_str else datetime.now()
                    except ValueError:
                        pub_date = datetime.now()

                    # Inventors
                    inventors = result.get("inventors", [])
                    if isinstance(inventors, list):
                        authors = ", ".join([inv.get("name", "") for inv in inventors if isinstance(inv, dict)])
                    else:
                        authors = "N/A"

                    # Classifications
                    classifications = result.get("classifications", {})
                    cpc_list = classifications.get("cpc", [])
                    cpc_str = ", ".join([c.get("code", "") for c in cpc_list if isinstance(c, dict)]) if cpc_list else "N/A"
                    
                    uspc_list = classifications.get("us", [])
                    uspc_str = ", ".join([u.get("code", "") for u in uspc_list if isinstance(u, dict)]) if uspc_list else "N/A"

                    # Abstract
                    abstract = f"{title}. {snippet}" if snippet else title
                    ai_summary = summarize_text(abstract) if snippet else None

                    # NEW: Extract assignee (company/owner)
                    assignee = None
                    assignees = result.get("assignees", [])
                    if isinstance(assignees, list) and len(assignees) > 0:
                        assignee = assignees[0].get("name", "N/A") if isinstance(assignees[0], dict) else "N/A"
                    
                    # NEW: Priority date
                    priority_date = result.get("priority_date", "N/A")
                    
                    # NEW: Patent family ID
                    patent_family_id = result.get("family_id", "N/A")
                    
                    # NEW: PDF URL
                    patent_pdf_url = result.get("pdf", None)
                    
                    # NEW: Thumbnail
                    thumbnail_url = result.get("thumbnail", None)
                    
                    # NEW: Citation count
                    cited_by_count = None
                    cited_by = result.get("cited_by", {})
                    if isinstance(cited_by, dict):
                        cited_by_count = cited_by.get("total", 0)

                    patents.append({
                        "type": "patent",
                        "title": title,
                        "abstract": abstract,
                        "summary": ai_summary,
                        "authors": authors if authors else "N/A",
                        "date": pub_date,
                        "source": "Google Patents",
                        "domain": domain,
                        "application_number": patent_id,
                        "application_status": result.get("status", "N/A"),
                        "publication_date": pub_date_str if pub_date_str else "N/A",
                        "uspc_classification": uspc_str,
                        "cpc_classifications": cpc_str,
                        # NEW fields
                        "assignee": assignee,
                        "priority_date": priority_date,
                        "patent_family_id": patent_family_id,
                        "patent_pdf_url": patent_pdf_url,
                        "thumbnail_url": thumbnail_url,
                        "cited_by_count": cited_by_count
                    })

                page += 1
                time.sleep(1)

            except requests.exceptions.RequestException as e:
                print(f"Error fetching patents for domain {domain}: {e}")
                break
            except Exception as e:
                print(f"Unexpected error processing patents for domain {domain}: {e}")
                break

        print(f"Fetched {len(patents)} patents for domain: {domain}")
        all_patents.extend(patents)

    return all_patents


def get_domain_id(db, domain_name):
    """Retrieves or creates a domain ID."""
    domain = db.query(Domain).filter(Domain.name == domain_name).first()
    if domain:
        return domain.id
    new_domain = Domain(name=domain_name)
    db.add(new_domain)
    db.commit()
    db.refresh(new_domain)
    return new_domain.id


def insert_items(items):
    """Inserts items into database with deduplication."""
    db = SessionLocal()
    try:
        inserted_count = 0
        for it in items:
            exists = db.query(Item).filter(Item.title == it["title"]).first()
            if exists:
                continue
                
            domain_id = get_domain_id(db, it["domain"])
            item = Item(
                type=it["type"],
                title=it["title"],
                abstract=it["abstract"],
                summary=it["summary"],
                authors=it["authors"],
                date=it["date"],
                source=it["source"],
                domain_id=domain_id,
                # Patent fields
                application_number=it.get("application_number"),
                application_status=it.get("application_status"),
                publication_date=it.get("publication_date"),
                uspc_classification=it.get("uspc_classification"),
                cpc_classifications=it.get("cpc_classifications"),
                assignee=it.get("assignee"),
                priority_date=it.get("priority_date"),
                patent_family_id=it.get("patent_family_id"),
                patent_pdf_url=it.get("patent_pdf_url"),
                thumbnail_url=it.get("thumbnail_url"),
                cited_by_count=it.get("cited_by_count"),
                # Paper fields
                arxiv_id=it.get("arxiv_id"),
                pdf_url=it.get("pdf_url"),
                doi=it.get("doi"),
                journal_ref=it.get("journal_ref"),
                categories=it.get("categories"),
                comment=it.get("comment")
            )
            db.add(item)
            inserted_count += 1
        db.commit()
        print(f"Inserted {inserted_count} new items successfully ✅")
    except Exception as e:
        db.rollback()
        print("Error inserting items:", e)
    finally:
        db.close()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    domains_list = [d.name for d in db.query(Domain).all()]
    if not domains_list:
        print("No domains found. Initializing with default domains...")
        default_domains = ["AI", "Robotics", "Quantum Computing", "Genetics", "Cybersecurity", "Blockchain"]
        for domain_name in default_domains:
            get_domain_id(db, domain_name)
        db.close()
        db = SessionLocal()
        domains_list = [d.name for d in db.query(Domain).all()]
        
    print(f"Using domains: {domains_list}")
    
    print("\n--- Fetching arXiv Papers ---")
    arxiv_papers = fetch_arxiv(domains_list, max_results=50)
    print(f"Fetched {len(arxiv_papers)} papers from arXiv.")
    
    print("\n--- Fetching Google Patents ---")
    google_patents = fetch_google_patents(domains_list, max_results=50)
    print(f"Fetched {len(google_patents)} patents from Google Patents.")
    
    all_items = arxiv_papers + google_patents
    print(f"\n--- Inserting {len(all_items)} total items into database ---")
    insert_items(all_items)
    
    print("\n✅ Data ingestion complete!")