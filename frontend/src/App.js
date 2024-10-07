// frontend/src/App.js
import React, { useEffect, useRef, useState } from 'react';
import {
  Container, Box, TextField, Button, CircularProgress, Typography, Select, MenuItem, FormControl, InputLabel,
} from '@mui/material';
import Article from './components/Article';
import { useAppContext } from './contexts/AppContext';
import './styles/App.css';

function App() {
  const { state, dispatch, searchArticlesWithOptions, fetchSummary, loadMoreArticles } = useAppContext();
  const { searchQuery, articles, selectedArticle, summaryPanelOpen, loading, error, page, hasMore, sort_by, order } = state;
  const [sortOrder, setSortOrder] = useState(order);
  const [sortBy, setSortBy] = useState(sort_by);

  const observer = useRef();

  // Handle search input
  const handleSearchInput = (event) => {
    dispatch({ type: 'SET_QUERY', payload: event.target.value });
  };

  // Trigger search when the sorting options change (automatically apply filters)
  useEffect(() => {
    if (searchQuery.trim()) {
      searchArticlesWithOptions(searchQuery, 1, 5, sortBy, sortOrder); // Start from page 1
    }
    // Reset the order to 'desc' when sorting by relevance (since order doesn't matter for relevance)
    if (sortBy === 'score') {
      setSortOrder('desc');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sortBy, sortOrder]); // Now only runs when sort options change

  // Manually trigger search when the user presses Enter or clicks the search button
  const handleSearch = () => {
    if (searchQuery.trim() === '') {
      dispatch({ type: 'SET_ERROR', payload: 'Please enter a search term' });
      return;
    }
    searchArticlesWithOptions(searchQuery, 1, 5, sortBy, sortOrder);
  };

  // Handle "Enter" key to trigger search
  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  // Intersection observer to detect scrolling to the end of the article list
  const lastArticleElementRef = useRef();
  useEffect(() => {
    if (loading || !hasMore) return;

    const observerCallback = (entries) => {
      if (entries[0].isIntersecting) {
        loadMoreArticles(searchQuery, page + 1, 5, sortBy, sortOrder);
      }
    };

    if (observer.current) observer.current.disconnect();

    observer.current = new IntersectionObserver(observerCallback);
    if (lastArticleElementRef.current) observer.current.observe(lastArticleElementRef.current);

  }, [loading, hasMore, searchQuery, page, sortBy, sortOrder, loadMoreArticles]);

  // Error fade-out effect
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        dispatch({ type: 'SET_ERROR', payload: null });
      }, 3000); // Fades out the error after 3 seconds

      return () => clearTimeout(timer); // Cleanup the timer if the component unmounts or if error changes
    }
  }, [error, dispatch]);

  return (
    <Container maxWidth="md" className="app-container">
      <Box className="sticky-search-bar">
        <Typography variant="h4" align="center" color="textPrimary" gutterBottom>
          News Aggregator
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
          <Button
            onClick={handleSearch}
            variant="contained"
            color="primary"
            className="search-button"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : 'Search'}
          </Button>
        </Box>

        {/* Sorting Options */}
        <Box className="filter-container"> {/* Add vertical spacing */}
          <FormControl variant="outlined" className="sort-select">
            <InputLabel id="sort-by-label">Sort By</InputLabel>
            <Select
              labelId="sort-by-label"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)} // Automatically trigger search on change
              label="Sort By"
            >
              <MenuItem value="score">Relevance</MenuItem>
              <MenuItem value="date">Date</MenuItem>
            </Select>
          </FormControl>

          {/* Conditionally show the "Order" dropdown only when sorting by date */}
          {sortBy === 'date' && (
            <FormControl variant="outlined" className="order-select">
              <InputLabel id="sort-order-label">Order</InputLabel>
              <Select
                labelId="sort-order-label"
                value={sortOrder}
                onChange={(e) => setSortOrder(e.target.value)} // Automatically trigger search on change
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
          articles.map((article, index) => {
            if (articles.length === index + 1) {
              return (
                <div ref={lastArticleElementRef} key={article._id}>
                  <Article article={article} fetchSummary={fetchSummary} />
                </div>
              );
            } else {
              return <Article key={article._id} article={article} fetchSummary={fetchSummary} />;
            }
          })
        ) : (
          <Typography align="center" color="textSecondary">
            {loading ? '' : 'No articles found. Try refining your search.'}
          </Typography>
        )}
      </Box>

      {/* Loading more articles */}
      {loading && <CircularProgress style={{ display: 'block', margin: '20px auto' }} />}

      {/* No more articles message */}
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
