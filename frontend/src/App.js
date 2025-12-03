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
    <Box sx={{ minHeight: '100vh' }}>
      <Navbar />
      <Container maxWidth="xl" sx={{ pt: 5, pb: 6 }}>
        <Grid container spacing={3}>
          {/* Sidebar */}
          <Grid item xs={12} md={3}>
            <Paper 
              elevation={0}
              sx={{ 
                p: 3, 
                borderRadius: 2,
                border: (theme) => theme.palette.mode === 'dark' ? '1px solid #2a2a2a' : '1px solid #e5e7eb',
                background: (theme) => theme.palette.mode === 'dark' ? '#141414' : '#ffffff',
                position: 'sticky',
                top: 80
              }}
            >
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 700, mb: 3 }}>
                Bộ Lọc
              </Typography>
              <Typography sx={{ mt: 2, mb: 1, fontWeight: 600, fontSize: '0.875rem', textTransform: 'uppercase', letterSpacing: 0.5, opacity: 0.7 }}>Sắp Xếp Theo</Typography>
              <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                <Select 
                  value={sortBy} 
                  onChange={(e) => setSortBy(e.target.value)}
                  sx={{ borderRadius: 1.5 }}
                >
                  <MenuItem value="score">Độ Liên Quan</MenuItem>
                  <MenuItem value="date">Ngày Tháng</MenuItem>
                </Select>
              </FormControl>
              {sortBy === 'date' && (
                <FormControl fullWidth size="small" sx={{ mb: 3 }}>
                  <Select 
                    value={sortOrder} 
                    onChange={(e) => setSortOrder(e.target.value)}
                    sx={{ borderRadius: 1.5 }}
                  >
                    <MenuItem value="asc">Cũ Nhất</MenuItem>
                    <MenuItem value="desc">Mới Nhất</MenuItem>
                  </Select>
                </FormControl>
              )}
              <Typography sx={{ fontWeight: 600, mb: 2, fontSize: '0.875rem', textTransform: 'uppercase', letterSpacing: 0.5, opacity: 0.7 }}>
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
                        size="small"
                        sx={{ 
                          '&.Mui-checked': {
                            color: (theme) => theme.palette.mode === 'dark' ? '#ffffff' : '#000000'
                          }
                        }}
                      />
                    }
                    label={<Typography sx={{ fontSize: '0.9rem' }}>{source}</Typography>}
                    sx={{ mb: 0.5 }}
                  />
                ))}
              </FormGroup>
            </Paper>
          </Grid>
          {/* Main Content */}
          <Grid item xs={12} md={9}>
            <Box sx={{ mb: 5 }}>
              <Typography 
                variant="h3" 
                align="center" 
                gutterBottom 
                sx={{ 
                  fontWeight: 800, 
                  letterSpacing: -2, 
                  mb: 1,
                  fontSize: { xs: '2.5rem', md: '3.5rem' },
                  background: (theme) => theme.palette.mode === 'dark' 
                    ? 'linear-gradient(135deg, #ffffff 0%, #a0a0a0 100%)'
                    : 'linear-gradient(135deg, #000000 0%, #4a4a4a 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                }}
              >
                Tin Nhanh Báo Lẹ
              </Typography>
              <Typography 
                align="center"
                sx={{
                  mb: 4,
                  opacity: 0.6,
                  fontSize: '0.95rem',
                  letterSpacing: 0.5
                }}
              >
                Tìm kiếm tin tức nhanh chóng và chính xác
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, maxWidth: 700, mx: 'auto' }}>
                <TextField
                  value={searchQuery}
                  onChange={handleSearchInput}
                  variant="outlined"
                  placeholder="Tìm một bài báo..."
                  onKeyDown={handleKeyDown}
                  fullWidth
                  sx={{ 
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                      background: (theme) => theme.palette.mode === 'dark' ? '#1a1a1a' : '#f9fafb',
                      '& fieldset': {
                        borderColor: (theme) => theme.palette.mode === 'dark' ? '#2a2a2a' : '#e5e7eb'
                      }
                    }
                  }}
                />
                <Button 
                  onClick={handleSearch} 
                  variant="contained" 
                  size="large" 
                  sx={{ 
                    borderRadius: 2, 
                    fontWeight: 600,
                    px: 4,
                    textTransform: 'none',
                    boxShadow: 'none',
                    '&:hover': {
                      boxShadow: 'none',
                      transform: 'translateY(-1px)'
                    },
                    transition: 'all 0.2s ease'
                  }}
                >
                  Tìm
                </Button>
              </Box>
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
