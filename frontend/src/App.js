// frontend/src/App.js
import React, { useEffect, useRef, useState } from 'react';
import {
  Container,
  Box,
  TextField,
  CircularProgress,
  Typography,
  Select,
  MenuItem,
  FormControl,
  Drawer,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Button,
} from '@mui/material';
import Article from './components/Article';
import { useAppContext } from './contexts/AppContext';
import './styles/App.css';

function App() {
  const { state, dispatch, searchArticlesWithOptions, fetchSummary, loadMoreArticles } = useAppContext();
  const { searchQuery, articles, selectedArticle, summaryPanelOpen, loading, error, page, hasMore, sort_by, order, sources } = state;
  const [sortOrder, setSortOrder] = useState(order);
  const [sortBy, setSortBy] = useState(sort_by);
  const [selectedSources, setSelectedSources] = useState(sources || []);

  const lastArticleElementRef = useRef();

  // Handle source filter toggle
  const handleSourceToggle = (source) => {
    const updatedSources = selectedSources.includes(source)
      ? selectedSources.filter((s) => s !== source)
      : [...selectedSources, source];
    setSelectedSources(updatedSources);
  };

  // Handle search input
  const handleSearchInput = (event) => {
    dispatch({ type: 'SET_QUERY', payload: event.target.value });
  };

  // Handle search action
  const handleSearch = () => {
    if (searchQuery.trim() === '') {
      dispatch({ type: 'SET_ERROR', payload: 'Please enter a search term' });
      return;
    }
    searchArticlesWithOptions(searchQuery, 1, 5, sortBy, sortOrder, selectedSources);
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  useEffect(() => {
    if (loading || !hasMore) return;

    const currentRef = lastArticleElementRef.current;

    const observerCallback = (entries) => {
      if (entries[0].isIntersecting) {
        loadMoreArticles(searchQuery, page, 5, sortBy, sortOrder, selectedSources);
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
  }, [loading, hasMore, searchQuery, page, sortBy, sortOrder, selectedSources, loadMoreArticles]);

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        dispatch({ type: 'SET_ERROR', payload: null });
      }, 3000);

      return () => clearTimeout(timer);
    }
  }, [error, dispatch]);

  // Filter articles by source
  const filteredArticles = articles.filter((article) =>
    selectedSources.includes(article.source)
  );

  return (
    <Container maxWidth="lg" className="app-container">
      <Box display="flex">
        {/* Sidebar */}
        <Drawer variant="permanent" anchor="left" classes={{ paper: 'sidebar-drawer' }}>
          <Box p={2} className="sidebar-container">
            <Typography variant="h6" gutterBottom>
              Filters
            </Typography>

            {/* Sort By */}
            <Typography className="filter-label">Sort By</Typography>
            <FormControl fullWidth className="compact-dropdown">
              <Select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="compact-dropdown"
              >
                <MenuItem value="score">Relevance</MenuItem>
                <MenuItem value="date">Date</MenuItem>
              </Select>
            </FormControl>

            {/* Order */}
            {sortBy === 'date' && (
              <FormControl fullWidth className="compact-dropdown">
                <Select
                  value={sortOrder}
                  onChange={(e) => setSortOrder(e.target.value)}
                  className="compact-dropdown"
                >
                  <MenuItem value="asc">Ascending</MenuItem>
                  <MenuItem value="desc">Descending</MenuItem>
                </Select>
              </FormControl>
            )}

            {/* Sources */}
            <Typography variant="subtitle1" gutterBottom>
              Sources
            </Typography>
            <FormGroup>
              {['VNExpress', 'Tuổi Trẻ', 'VietnamNet', 'Thanh Niên', 'Dân Trí'].map((source) => (
                <FormControlLabel
                  key={source}
                  control={
                    <Checkbox
                      checked={selectedSources.includes(source)}
                      onChange={() => handleSourceToggle(source)}
                    />
                  }
                  label={source}
                />
              ))}
            </FormGroup>
          </Box>
        </Drawer>

        {/* Main Content */}
        <Box flex="1" ml={30} className="main-content" display="flex" flexDirection="column" alignItems="center">
          <Box className="fixed-panel">
            <Typography className="app-title" variant="h4" align="center" color="textPrimary" gutterBottom>
              Tin Nhanh Báo Lẹ
            </Typography>
            <TextField
              value={searchQuery}
              onChange={handleSearchInput}
              variant="outlined"
              placeholder="Search for news articles..."
              onKeyDown={handleKeyDown}
              className="search-input"
            />
          </Box>

          {/* Articles List */}
          <Box className="articles-list">
            {filteredArticles.length > 0 ? (
              filteredArticles.map((article, index) => (
                <div
                  ref={index === filteredArticles.length - 1 ? lastArticleElementRef : null}
                  key={article.id || article._id}
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

          {/* No More Articles */}
          {!loading && !hasMore && (
            <Typography align="center" color="textSecondary">
              No more articles to load.
            </Typography>
          )}

          {/* Summary Panel */}
          {summaryPanelOpen && selectedArticle && (
            <Box className="summary-panel">
              <Button onClick={() => dispatch({ type: 'CLOSE_SUMMARY_PANEL' })}>Close</Button>
              <Typography variant="h6">{selectedArticle.title}</Typography>
              <Typography variant="body1">{selectedArticle.summary}</Typography>
            </Box>
          )}
        </Box>
      </Box>
    </Container>
  );
}

export default App;
