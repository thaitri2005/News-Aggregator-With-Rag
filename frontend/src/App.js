import React from 'react';
import {
  Container, TextField, Button, CircularProgress, Box, Typography, Card, CardContent, CardActions, Link,
} from '@mui/material';
import { useAppContext } from './AppContext';
import './App.css';

function App() {
  const { state, dispatch, searchArticles, fetchSummary } = useAppContext();
  const { searchQuery, articles, selectedArticle, summaryPanelOpen, loading, error } = state;

  const handleSearchInput = (event) => {
    dispatch({ type: 'SET_QUERY', payload: event.target.value });
  };

  const handleSearch = () => {
    searchArticles(searchQuery);
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

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
            articles.map((article) => (
              <Card key={article._id} className="article-card">
                <CardContent>
                  <Typography variant="h6" color="primary">{article.title}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    {new Date(article.date).toLocaleDateString()}
                  </Typography>
                  <Link href={article.source_url} target="_blank" rel="noopener">
                    Read More
                  </Link>
                </CardContent>
                <CardActions>
                  <Button
                    size="small"
                    color="primary"
                    onClick={() => fetchSummary(article)}
                  >
                    View Summary
                  </Button>
                </CardActions>
              </Card>
            ))
          ) : (
            <Typography>No articles found</Typography>
          )}
        </Box>
      </Box>

      {/* Summary Panel */}
      {summaryPanelOpen && selectedArticle && (
        <Box className="summary-panel">
          <Button onClick={() => dispatch({ type: 'CLOSE_SUMMARY_PANEL' })}>Close</Button>
          <Typography variant="h6">{selectedArticle.title}</Typography>
          <Typography variant="body1">{selectedArticle.summary}</Typography>
        </Box>
      )}
    </Container>
  );
}

export default App;
