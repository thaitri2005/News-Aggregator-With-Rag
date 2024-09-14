import React, { useState } from 'react';
import axios from 'axios';
import {
  Container, TextField, Button, CircularProgress, Box, Typography, Card, CardContent, CardActions, Link,
} from '@mui/material';
import './App.css'; // Assuming your CSS

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
    } catch (error) {
      setError('An error occurred while fetching the articles');
    } finally {
      setLoading(false);
    }
  };

  // Function to fetch summary for an article when "<" button is clicked
  const fetchSummary = async (article) => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/api/summarize', {
        article_text: article.content,
      });
      setSelectedArticle({
        ...article,
        summary: response.data.summary || 'No summary available',
      });
      setSummaryPanelOpen(true);
    } catch (error) {
      setError('Failed to load summary');
    } finally {
      setLoading(false);
    }
  };

  // Function to close the summary panel
  const closeSummaryPanel = () => {
    setSummaryPanelOpen(false); // Close the summary panel
    setSelectedArticle(null); // Deselect the article
  };

  return (
    <Container maxWidth="md" className="app-container">
      <Box my={4}>
        <Typography variant="h4" align="center" color="textPrimary" gutterBottom>
          News Aggregator
        </Typography>

        {/* Search Input Field */}
        <Box display="flex" justifyContent="center" mb={2}>
          <TextField
            value={searchQuery}
            onChange={handleSearchInput}
            variant="outlined"
            placeholder="Search for news articles..."
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
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
          <Button onClick={closeSummaryPanel}>Close</Button>
          <Typography variant="h6">{selectedArticle.title}</Typography>
          <Typography variant="body1">{selectedArticle.summary}</Typography>
        </Box>
      )}
    </Container>
  );
}

export default App;
