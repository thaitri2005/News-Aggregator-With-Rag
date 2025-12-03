/* frontend/src/Article.js */
import React from 'react';
import { Card, Typography, CardActions, Button, Link, CardHeader } from '@mui/material';
import PropTypes from 'prop-types';

const Article = React.memo(({ article, fetchSummary }) => {
  if (!article) return null; // Return null if no article is passed
  
  const { _id, title, date, source_url } = article;

  return (
    <Card
      key={_id}
      className="article-card"
      role="article"
      aria-labelledby={`article-title-${_id}`}
      elevation={0}
      sx={{
        borderRadius: 2,
        mb: 2,
        border: (theme) => theme.palette.mode === 'dark' ? '1px solid #2a2a2a' : '1px solid #e5e7eb',
        transition: 'all 0.2s ease',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: (theme) => theme.palette.mode === 'dark' 
            ? '0 8px 24px rgba(0,0,0,0.4)'
            : '0 8px 24px rgba(0,0,0,0.08)',
          borderColor: (theme) => theme.palette.mode === 'dark' ? '#3a3a3a' : '#d1d5db'
        }
      }}
    >
      <CardHeader
        title={
          <Typography 
            variant="h6" 
            id={`article-title-${_id}`}
            sx={{ 
              fontWeight: 600, 
              fontSize: '1.1rem',
              lineHeight: 1.4
            }}
          >
            {title || 'Untitled'}
          </Typography>
        }
        subheader={
          <Typography 
            variant="caption" 
            color="text.secondary"
            sx={{ fontSize: '0.8rem', mt: 0.5 }}
          >
            {date ? new Date(date).toLocaleDateString('vi-VN') : 'No date available'}
          </Typography>
        }
        sx={{ pb: 1 }}
      />
      <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
        {source_url && (
          <Link 
            href={source_url} 
            target="_blank" 
            rel="noopener noreferrer"
            underline="hover"
            sx={{ 
              fontSize: '0.875rem',
              fontWeight: 500,
              color: (theme) => theme.palette.mode === 'dark' ? '#9ca3af' : '#6b7280'
            }}
          >
            Đọc Thêm →
          </Link>
        )}
        <Button
          size="small"
          variant="outlined"
          onClick={() => fetchSummary(article)}
          aria-label={`View summary of ${title}`}
          sx={{ 
            borderRadius: 1.5,
            textTransform: 'none',
            fontWeight: 600,
            px: 2,
            borderColor: (theme) => theme.palette.mode === 'dark' ? '#3a3a3a' : '#e5e7eb',
            '&:hover': {
              borderColor: (theme) => theme.palette.mode === 'dark' ? '#ffffff' : '#000000',
              background: 'transparent'
            }
          }}
        >
          Tóm Tắt
        </Button>
      </CardActions>
    </Card>
  );
});

Article.propTypes = {
  article: PropTypes.object.isRequired,
  fetchSummary: PropTypes.func.isRequired,
};

export default Article;
