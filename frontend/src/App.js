/* frontend/src/App.js */
import React, { useEffect, useRef } from 'react';
import { Container, Box, Typography, CircularProgress } from '@mui/material';
import Article from './components/Article'; 
import SearchBar from './components/SearchBar';
import SummaryPanel from './components/SummaryPanel';
import { useAppContext } from './contexts/AppContext';
import './styles/App.css';

function App() {
  const { state, dispatch, searchArticles, fetchSummary, loadMoreArticles } = useAppContext();
  const { searchQuery, articles, selectedArticle, summaryPanelOpen, loading, error, page, hasMore } = state;
  const observer = useRef();

  const handleSearchInput = (event) => dispatch({ type: 'SET_QUERY', payload: event.target.value });
  const handleSearch = () => searchArticles(searchQuery, 1);
  const handleKeyDown = (event) => { if (event.key === 'Enter') handleSearch(); };

  const lastArticleElementRef = useRef();
  useEffect(() => {
    if (loading || !hasMore) return;
    const observerCallback = (entries) => { if (entries[0].isIntersecting) loadMoreArticles(searchQuery, page + 1); };
    if (observer.current) observer.current.disconnect();
    observer.current = new IntersectionObserver(observerCallback);
    if (lastArticleElementRef.current) observer.current.observe(lastArticleElementRef.current);
  }, [loading, hasMore, searchQuery, page, loadMoreArticles]);

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        dispatch({ type: 'SET_ERROR', payload: null });
      }, 3000);

      return () => clearTimeout(timer); // Cleanup the timer if the component unmounts or if error changes
    }
  }, [error, dispatch]); // Include dispatch in the dependency array


  return (
    <Container maxWidth="md" className="app-container">
      <Box className="sticky-search-bar">
        <Typography variant="h4" align="center" color="textPrimary" gutterBottom>News Aggregator</Typography>
        <SearchBar
          searchQuery={searchQuery}
          handleSearchInput={handleSearchInput}
          handleKeyDown={handleKeyDown}
          handleSearch={handleSearch}
          loading={loading}
        />
        {error && <Typography className="error-message" align="center">{error}</Typography>}
      </Box>

      <Box className="articles-list">
        {articles.length > 0 ? (
          articles.map((article, index) => (
            <div ref={articles.length === index + 1 ? lastArticleElementRef : null} key={article._id}>
              <Article article={article} fetchSummary={fetchSummary} />
            </div>
          ))
        ) : (
          <Typography align="center" color="textSecondary">{loading ? '' : 'No articles found. Try refining your search.'}</Typography>
        )}
      </Box>

      {loading && <CircularProgress style={{ display: 'block', margin: '20px auto' }} />}
      {!loading && !hasMore && <Typography align="center" color="textSecondary">No more articles to load.</Typography>}

      {summaryPanelOpen && selectedArticle && <SummaryPanel selectedArticle={selectedArticle} dispatch={dispatch} />}
    </Container>
  );
}

export default App;
