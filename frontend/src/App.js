import React, { useEffect, useRef } from 'react';
import {
  Container, Box, TextField, Button, CircularProgress, Typography,
} from '@mui/material';
import Article from './Article'; // Import the optimized Article component
import { useAppContext } from './AppContext';
import './App.css';

function App() {
  const { state, dispatch, searchArticles, fetchSummary, loadMoreArticles } = useAppContext();
  const { searchQuery, articles, selectedArticle, summaryPanelOpen, loading, error, page, hasMore } = state;
  const observer = useRef();

  // Handle search input
  const handleSearchInput = (event) => {
    dispatch({ type: 'SET_QUERY', payload: event.target.value });
  };

  // Trigger search
  const handleSearch = () => {
    if (searchQuery.trim() === '') {
      dispatch({ type: 'SET_ERROR', payload: 'Please enter a search term' });
      return;
    }
    searchArticles(searchQuery, 1); // Start from page 1
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
    if (loading || !hasMore) return; // Stop if already loading or no more articles

    const observerCallback = (entries) => {
      if (entries[0].isIntersecting) {
        loadMoreArticles(searchQuery, page + 1); // Load next page when scrolling reaches the end
      }
    };

    if (observer.current) observer.current.disconnect();

    observer.current = new IntersectionObserver(observerCallback);
    if (lastArticleElementRef.current) observer.current.observe(lastArticleElementRef.current);

  }, [loading, hasMore, searchQuery, page, loadMoreArticles]);

  return (
    <Container maxWidth="md" className="app-container">
      <Box my={4}>
        <Typography variant="h4" align="center" color="textPrimary" gutterBottom>
          News Aggregator
        </Typography>

        {/* Search Input */}
        <Box display="flex" justifyContent="center" mb={2}>
          <TextField
            value={searchQuery}
            onChange={handleSearchInput}
            variant="outlined"
            placeholder="Search for news articles..."
            onKeyDown={handleKeyDown}
            style={{ width: '60%' }}
          />
          <Button
            onClick={handleSearch}
            variant="contained"
            color="primary"
            style={{ marginLeft: '10px' }}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : 'Search'}
          </Button>
        </Box>

        {/* Error Message */}
        {error && <Typography color="error" align="center">{error}</Typography>}

        {/* Articles List */}
        <Box>
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
      </Box>

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
