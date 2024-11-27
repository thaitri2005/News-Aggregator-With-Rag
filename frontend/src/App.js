// frontend/src/App.js
import React, { useEffect, useRef, useState } from 'react';
import {
  Container, Box, TextField, Button, CircularProgress, Typography, Select, MenuItem, FormControl, InputLabel
} from '@mui/material';
import Article from './components/Article';
import { useAppContext } from './contexts/AppContext';
import './styles/App.css';

function App() {
  const { state, dispatch, searchArticlesWithOptions, fetchSummary, loadMoreArticles } = useAppContext();
  const { searchQuery, articles, selectedArticle, summaryPanelOpen, loading, error, page, hasMore, sort_by, order } = state;
  const [sortOrder, setSortOrder] = useState(order);
  const [sortBy, setSortBy] = useState(sort_by);

  const lastArticleElementRef = useRef();

  // Handle search input
  const handleSearchInput = (event) => {
    dispatch({ type: 'SET_QUERY', payload: event.target.value });
  };

  // Trigger search when sort options change
  useEffect(() => {
    if (searchQuery.trim()) {
      searchArticlesWithOptions(searchQuery, 1, 5, sortBy, sortOrder);
    }
    // Reset order to 'desc' for relevance sorting
    if (sortBy === 'score') {
      setSortOrder('desc');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sortBy, sortOrder]);

  // Handle search on button click or "Enter" key press
  const handleSearch = () => {
    if (searchQuery.trim() === '') {
      dispatch({ type: 'SET_ERROR', payload: 'Please enter a search term' });
      return;
    }
    searchArticlesWithOptions(searchQuery, 1, 5, sortBy, sortOrder);
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  useEffect(() => {
    if (loading || !hasMore) return;
  
    // Store the ref value in a local variable to ensure stability during cleanup
    const currentRef = lastArticleElementRef.current;
  
    const observerCallback = (entries) => {
      if (entries[0].isIntersecting) {
        loadMoreArticles(searchQuery, page, 5, sortBy, sortOrder);
      }
    };
  
    const observer = new IntersectionObserver(observerCallback, { threshold: 0.1 });
    if (currentRef) {
      observer.observe(currentRef);
    }
  
    return () => {
      if (currentRef) {
        observer.unobserve(currentRef);
      }
    };
  }, [loading, hasMore, searchQuery, page, sortBy, sortOrder, loadMoreArticles]);  

  // Error fade-out effect
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        dispatch({ type: 'SET_ERROR', payload: null });
      }, 3000);

      return () => clearTimeout(timer);
    }
  }, [error, dispatch]);

  return (
    <Container maxWidth="md" className="app-container">
      <Box className="sticky-search-bar">
        <Typography variant="h4" align="center" color="textPrimary" gutterBottom>
          Vietnamese News Aggregator
        </Typography>

        {/* Search Input */}
        <Box className="search-container">
          <TextField
            value={searchQuery}
            onChange={handleSearchInput}
            variant="outlined"
            placeholder="Search for news articles..."
            onKeyDown={handleKeyDown}
            className="search-input"
          />
        </Box>

        {/* Sorting Options */}
        <Box className="filter-container">
          <FormControl variant="outlined" className="sort-select">
            <InputLabel id="sort-by-label">Sort By</InputLabel>
            <Select
              labelId="sort-by-label"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              label="Sort By"
            >
              <MenuItem value="score">Relevance</MenuItem>
              <MenuItem value="date">Date</MenuItem>
            </Select>
          </FormControl>
          {sortBy === 'date' && (
            <FormControl variant="outlined" className="order-select">
              <InputLabel id="sort-order-label">Order</InputLabel>
              <Select
                labelId="sort-order-label"
                value={sortOrder}
                onChange={(e) => setSortOrder(e.target.value)}
                label="Order"
              >
                <MenuItem value="asc">Ascending</MenuItem>
                <MenuItem value="desc">Descending</MenuItem>
              </Select>
            </FormControl>
          )}
        </Box>

        {/* Error Message */}
        {error && <Typography className="error-message" align="center">{error}</Typography>}
      </Box>

      {/* Articles List */}
      <Box className="articles-list">
        {articles.length > 0 ? (
          articles.map((article, index) => (
            <div
              ref={index === articles.length - 1 ? lastArticleElementRef : null}
              key={article.id || article._id} // Ensure consistent IDs
            >
              <Article article={article} fetchSummary={fetchSummary} />
            </div>
          ))
        ) : (
          <Typography align="center" color="textSecondary">
            {loading ? '' : 'No articles found. Try refining your search.'}
          </Typography>
        )}
      </Box>

      {/* Loading Spinner */}
      {loading && <CircularProgress style={{ display: 'block', margin: '20px auto' }} />}

      {/* No More Articles Message */}
      {!loading && !hasMore && (
        <Typography align="center" color="textSecondary">
          No more articles to load.
        </Typography>
      )}

      {/* Summary Panel */}
      {summaryPanelOpen && selectedArticle && (
        <Box className="summary-panel" role="complementary" aria-label="Summary panel">
          <Button onClick={() => dispatch({ type: 'CLOSE_SUMMARY_PANEL' })}>Close</Button>
          <Typography variant="h6">{selectedArticle.title}</Typography>
          <Typography variant="body1">{selectedArticle.summary}</Typography>
        </Box>
      )}
    </Container>
  );
}

export default App;
