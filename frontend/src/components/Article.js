/* frontend/src/Article.js */
import React from 'react';
import { Card, CardContent, Typography, CardActions, Button, Link } from '@mui/material';
import PropTypes from 'prop-types';

const Article = React.memo(({ article, fetchSummary }) => {
  if (!article) return null; // Return null if no article is passed
  
  const { _id, title, date, source_url } = article;

  return (
    <Card key={_id} className="article-card" role="article" aria-labelledby={`article-title-${_id}`}>
      <CardContent>
        <Typography variant="h6" color="primary" id={`article-title-${_id}`}>
          {title || 'Untitled'}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          {date ? new Date(date).toLocaleDateString() : 'No date available'}
        </Typography>
        {source_url && (
          <Link href={source_url} target="_blank" rel="noopener noreferrer">
            Đọc Thêm
          </Link>
        )}
      </CardContent>
      <CardActions>
        <Button
          size="small"
          color="primary"
          onClick={() => fetchSummary(article)}
          aria-label={`View summary of ${title}`}
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
