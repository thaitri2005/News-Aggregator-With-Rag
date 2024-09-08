import React, { useEffect, useState } from 'react';
import axios from 'axios';

function App() {
  const [searchQuery, setSearchQuery] = useState('');  // State to store the search query
  const [articles, setArticles] = useState([]);  // State to store the articles
  const [loading, setLoading] = useState(false); // State for loading indicator
  const [error, setError] = useState(null);      // State for handling errors

  // Function to handle the search input change
  const handleSearchInput = (event) => {
    setSearchQuery(event.target.value);
  };

  // Function to trigger search on pressing Enter
  const handleSearch = () => {
    if (searchQuery.trim() === '') return; // Prevent empty searches

    setLoading(true);
    setError(null);

    // Fetch articles from the backend using the /retrieve API
    axios.post('http://localhost:5000/api/retrieve', {
      query: searchQuery,
      page: 1,
      limit: 10
    })
    .then((response) => {
      setArticles(response.data); // Store the articles in the state
      setLoading(false);
    })
    .catch((error) => {
      setError('An error occurred while fetching the articles');
      setLoading(false);
    });
  };

  // Function to handle pressing "Enter" key in search
  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div>
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
      <div>
        {articles.length > 0 ? (
          articles.map((article) => (
            <div key={article._id} className="article">
              <h2>{article.title}</h2>
              <p>Date: {new Date(article.date).toLocaleDateString()}</p>
              <a href={article.source_url} target="_blank" rel="noopener noreferrer">Read More</a>
            </div>
          ))
        ) : (
          <p>No articles found</p>
        )}
      </div>
    </div>
  );
}

export default App;
