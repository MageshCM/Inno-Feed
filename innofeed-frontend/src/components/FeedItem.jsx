import React from 'react';
import './FeedItem.css';

function FeedItem({ item }) {
  const formattedDate = item.date ? new Date(item.date).toLocaleDateString() : 'N/A';

  return (
    <div className="feed-item">
      <div className="item-header">
        <span className={`item-type ${item.type}`}>{item.type.toUpperCase()}</span>
        <h3 className="item-title">{item.title}</h3>
      </div>
      
      <p className="item-summary">{item.summary || item.abstract || 'No summary available'}</p>
      
      <div className="item-details">
        <p><strong>Authors:</strong> {item.authors || 'N/A'}</p>
        <p><strong>Source:</strong> {item.source}</p>
        <p><strong>Published Date:</strong> {formattedDate}</p>

        {/* PAPER-SPECIFIC FIELDS */}
        {item.type === 'paper' && (
          <div className="paper-specific-details">
            {item.arxiv_id && (
              <p><strong>arXiv ID:</strong> {item.arxiv_id}</p>
            )}
            
            {item.doi && item.doi !== 'N/A' && (
              <p>
                <strong>DOI:</strong>{' '}
                <a 
                  href={`https://doi.org/${item.doi}`} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="doi-link"
                >
                  {item.doi}
                </a>
              </p>
            )}
            
            {item.categories && (
              <p><strong>Categories:</strong> {item.categories}</p>
            )}
            
            {item.journal_ref && item.journal_ref !== 'N/A' && (
              <p><strong>Journal Reference:</strong> {item.journal_ref}</p>
            )}
            
            {item.comment && item.comment !== 'N/A' && (
              <p><strong>Comment:</strong> {item.comment}</p>
            )}
            
            {item.pdf_url && (
              <a 
                href={item.pdf_url} 
                target="_blank" 
                rel="noopener noreferrer" 
                className="pdf-link"
              >
                📄 Download PDF
              </a>
            )}
          </div>
        )}

        {/* PATENT-SPECIFIC FIELDS */}
        {item.type === 'patent' && (
          <div className="patent-specific-details">
            {item.application_number && (
              <p><strong>Application Number:</strong> {item.application_number}</p>
            )}
            
            {item.assignee && item.assignee !== 'N/A' && (
              <p><strong>Assignee:</strong> {item.assignee}</p>
            )}
            
            {item.application_status && (
              <p><strong>Application Status:</strong> {item.application_status}</p>
            )}
            
            {item.publication_date && item.publication_date !== 'N/A' && (
              <p><strong>Publication Date:</strong> {item.publication_date}</p>
            )}
            
            {item.priority_date && item.priority_date !== 'N/A' && (
              <p><strong>Priority Date:</strong> {item.priority_date}</p>
            )}
            
            {item.patent_family_id && item.patent_family_id !== 'N/A' && (
              <p><strong>Patent Family ID:</strong> {item.patent_family_id}</p>
            )}
            
            {item.cited_by_count !== null && item.cited_by_count !== undefined && item.cited_by_count > 0 && (
              <p><strong>Citations:</strong> {item.cited_by_count}</p>
            )}
            
            {item.uspc_classification && item.uspc_classification !== 'N/A' && (
              <p><strong>USPC Classification:</strong> {item.uspc_classification}</p>
            )}
            
            {item.cpc_classifications && item.cpc_classifications !== 'N/A' && (
              <p><strong>CPC Classifications:</strong> {item.cpc_classifications}</p>
            )}
            
            {item.patent_pdf_url && (
              <a 
                href={item.patent_pdf_url} 
                target="_blank" 
                rel="noopener noreferrer" 
                className="pdf-link"
              >
                📄 Download Patent PDF
              </a>
            )}
            
            {item.thumbnail_url && (
              <div className="patent-thumbnail">
                <img 
                  src={item.thumbnail_url} 
                  alt="Patent diagram" 
                  loading="lazy"
                  onError={(e) => {
                    e.target.style.display = 'none';
                  }}
                />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default FeedItem;