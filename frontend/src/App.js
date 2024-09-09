import React, { useState } from 'react';
import axios from 'axios';
import './index.css';

function App() {
  const [searchQuery, setSearchQuery] = useState('');  // State to store the search query
  const [articles, setArticles] = useState([]);  // State to store the articles
  const [loading, setLoading] = useState(false); // State for loading indicator
  const [error, setError] = useState(null);      // State for handling errors
  const [selectedArticle, setSelectedArticle] = useState(null); // Track the selected article for summary
  const [summaryPanelOpen, setSummaryPanelOpen] = useState(false); // Track if the summary panel is open

  // Function to handle the search input change
  const handleSearchInput = (event) => {
    setSearchQuery(event.target.value);
  };

  // Function to trigger search
  const handleSearch = async () => {
    if (searchQuery.trim() === '') return; // Prevent empty searches

    setLoading(true);
    setError(null);

    try {
      // Fetch articles from the backend using the /retrieve API
      const response = await axios.post('http://localhost:5000/api/retrieve', {
        query: searchQuery,
        page: 1,
        limit: 5  // You can set any limit here
      });
      setArticles(response.data);
      setLoading(false);
    } catch (error) {
      setError('An error occurred while fetching the articles');
      setLoading(false);
    }
  };

  // Function to handle pressing "Enter" key in search
  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  // Function to fetch summary for an article when the "<" button is clicked
  const fetchSummary = async (article) => {
    setLoading(true); // Show loading indicator when fetching summary
    try {
      const response = await axios.post('http://localhost:5000/api/summarize', {
        article_text: article.content,  // Assuming article.content is passed for summarization
      });
      setSelectedArticle({
        ...article,
        summary: response.data.summary || 'No summary available',
      });
      setLoading(false);
      setSummaryPanelOpen(true); // Open the summary panel when the summary is ready
    } catch (error) {
      setError('Failed to load summary');
      setLoading(false);
    }
  };

  // Function to close the summary panel
  const closeSummaryPanel = () => {
    setSummaryPanelOpen(false); // Close the summary panel
    setSelectedArticle(null); // Deselect the article
  };

  return (
    <div className="app-container">
      <h1>News Aggregator</h1>
      {/* Search Input Field */}
      <input 
        type="text" 
        value={searchQuery} 
        onChange={handleSearchInput} 
        onKeyDown={handleKeyDown} 
        placeholder="Search for news articles..." 
      />
      <button onClick={handleSearch}>Search</button>

      {/* Display loading state */}
      {loading && <p>Loading...</p>}

      {/* Display error message if any */}
      {error && <p>{error}</p>}

      {/* Display list of articles */}
      <div className="articles-container">
        {articles.length > 0 ? (
          articles.map((article) => (
            <div key={article._id} className={`article ${summaryPanelOpen ? 'shifted' : ''}`}>
              <h2>{article.title}</h2>
              <p>Date: {new Date(article.date).toLocaleDateString()}</p>
              <a href={article.source_url} target="_blank" rel="noopener noreferrer">Read More</a>
              <button className="summary-button" onClick={() => fetchSummary(article)}>{'<'}</button>
            </div>
          ))
        ) : (
          <p>No articles found</p>
        )}
      </div>

      {/* Summary Panel */}
      <div className={`summary-panel ${summaryPanelOpen ? 'open' : ''}`}>
        <button className="close-panel-button" onClick={closeSummaryPanel}>{'>'}</button>
        {selectedArticle && (
          <>
            <h3>Summary for: {selectedArticle.title}</h3>
            <p>{selectedArticle.summary}</p>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
