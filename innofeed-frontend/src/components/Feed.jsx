import React from 'react';
import FeedItem from './FeedItem';
import './Feed.css';

function Feed({ feedData }) {
  if (!feedData || feedData.length === 0) {
    return <p className="no-data">No feed items to display. Try setting your preferences.</p>;
  }

  return (
    <div className="feed-container">
      {feedData.map((item) => (
        <FeedItem key={item.id} item={item} />
      ))}
    </div>
  );
}

export default Feed;