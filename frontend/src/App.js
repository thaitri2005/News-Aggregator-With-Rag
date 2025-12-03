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
  FormGroup,
  FormControlLabel,
  Checkbox,
  Button,
  Grid,
  Paper,
} from '@mui/material';
import Navbar from './components/Navbar';
import Article from './components/Article';
import SummaryPanel from './components/SummaryPanel';
import { useAppContext } from './contexts/AppContext';
import './styles/App.css';

function App() {
  const { state, dispatch, searchArticlesWithOptions, fetchSummary, loadMoreArticles } = useAppContext();
  const { searchQuery, articles, selectedArticle, summaryPanelOpen, loading, error, page, hasMore, sort_by, order, sources } = state;
  const [sortOrder, setSortOrder] = useState(order);
  const [sortBy, setSortBy] = useState(sort_by);
  const [selectedSources, setSelectedSources] = useState(sources || []);
  const lastArticleElementRef = useRef();

  // ...existing logic for handlers and effects...
  const handleSourceToggle = (source) => {
    const updatedSources = selectedSources.includes(source)
      ? selectedSources.filter((s) => s !== source)
      : [...selectedSources, source];
    setSelectedSources(updatedSources);
  };
  const handleSearchInput = (event) => {
    dispatch({ type: 'SET_QUERY', payload: event.target.value });
  };
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
  const filteredArticles = articles.filter((article) => selectedSources.includes(article.source));

  return (
    <Box sx={{ minHeight: '100vh', background: 'linear-gradient(135deg, #e3f2fd 0%, #f8fafc 100%)' }}>
      <Navbar />
      <Container maxWidth="xl" sx={{ pt: 4 }}>
        <Grid container spacing={4}>
          {/* Sidebar */}
          <Grid item xs={12} md={3}>
            <Paper elevation={6} sx={{ p: 3, borderRadius: 4, background: 'rgba(255,255,255,0.85)', boxShadow: '0 8px 32px 0 rgba(31,38,135,0.15)' }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 700, color: '#1a73e8' }}>
                Bộ Lọc
              </Typography>
              <Typography className="filter-label" sx={{ mt: 2, mb: 1, fontWeight: 600 }}>Sắp Xếp Theo</Typography>
              <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                <Select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                  <MenuItem value="score">Độ Liên Quan</MenuItem>
                  <MenuItem value="date">Ngày Tháng</MenuItem>
                </Select>
              </FormControl>
              {sortBy === 'date' && (
                <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                  <Select value={sortOrder} onChange={(e) => setSortOrder(e.target.value)}>
                    <MenuItem value="asc">Cũ Nhất</MenuItem>
                    <MenuItem value="desc">Mới Nhất</MenuItem>
                  </Select>
                </FormControl>
              )}
              <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>
                Nguồn
              </Typography>
              <FormGroup>
                {['VNExpress', 'Tuổi Trẻ', 'VietnamNet', 'Thanh Niên', 'Dân Trí'].map((source) => (
                  <FormControlLabel
                    key={source}
                    control={
                      <Checkbox
                        checked={selectedSources.includes(source)}
                        onChange={() => handleSourceToggle(source)}
                        sx={{ color: '#1a73e8' }}
                      />
                    }
                    label={source}
                  />
                ))}
              </FormGroup>
            </Paper>
          </Grid>
          {/* Main Content */}
          <Grid item xs={12} md={9}>
            <Box sx={{ mb: 4, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Typography className="app-title" variant="h3" align="center" color="primary" gutterBottom sx={{ fontWeight: 800, letterSpacing: 1, mb: 2, textShadow: '0 2px 8px #b3e5fc' }}>
                Tin Nhanh Báo Lẹ
              </Typography>
              <TextField
                value={searchQuery}
                onChange={handleSearchInput}
                variant="outlined"
                placeholder="Tìm một bài báo..."
                onKeyDown={handleKeyDown}
                sx={{ width: '100%', maxWidth: 600, borderRadius: 8, background: '#fff', boxShadow: '0 2px 8px #b3e5fc' }}
                InputProps={{ style: { borderRadius: 30, fontSize: '1.1rem', padding: '10px 20px' } }}
              />
              <Button onClick={handleSearch} variant="contained" size="large" sx={{ mt: 2, borderRadius: 8, fontWeight: 700, background: 'linear-gradient(90deg, #1a73e8 0%, #2196f3 100%)', color: '#fff', boxShadow: '0 4px 16px #90caf9' }}>
                Tìm kiếm
              </Button>
            </Box>
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
                <Typography align="center" color="textSecondary" sx={{ fontSize: '1.2rem', mt: 4 }}>
                  {loading ? '' : 'Không tìm được bài báo nào. Hãy thử lại với từ khoá khác.'}
                </Typography>
              )}
            </Box>
            {loading && <CircularProgress style={{ display: 'block', margin: '20px auto' }} />}
            {!loading && !hasMore && (
              <Typography align="center" color="textSecondary" sx={{ mt: 2 }}>
                Không còn bài báo nào để tải thêm.
              </Typography>
            )}
            {/* Summary Dialog */}
            <SummaryPanel
              open={Boolean(summaryPanelOpen && selectedArticle)}
              selectedArticle={selectedArticle}
              onClose={() => dispatch({ type: 'CLOSE_SUMMARY_PANEL' })}
            />
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}

export default App;
