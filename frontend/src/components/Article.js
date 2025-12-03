/* frontend/src/Article.js */
import React from 'react';
import { Card, CardContent, Typography, CardActions, Button, Link, CardHeader } from '@mui/material';
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
      sx={{
        borderRadius: 3,
        boxShadow: '0 8px 24px rgba(26,115,232,0.15)',
        transition: 'transform 0.25s ease, box-shadow 0.25s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: '0 12px 30px rgba(26,115,232,0.25)'
        }
      }}
    >
      <CardHeader
        title={<Typography variant="h6" color="primary" id={`article-title-${_id}`}>{title || 'Untitled'}</Typography>}
        subheader={<Typography variant="caption" color="text.secondary">{date ? new Date(date).toLocaleDateString() : 'No date available'}</Typography>}
      />
      <CardContent>
        {source_url && (
          <Link href={source_url} target="_blank" rel="noopener noreferrer">
            Đọc Thêm
          </Link>
        )}
      </CardContent>
      <CardActions sx={{ justifyContent: 'flex-end' }}>
        <Button
          size="small"
          variant="contained"
          onClick={() => fetchSummary(article)}
          aria-label={`View summary of ${title}`}
          sx={{ borderRadius: 2 }}
        >
          Xem Tóm Tắt
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
