// frontend/src/services/api.js
import axios from 'axios';

// API base URL
const API_BASE_URL = 'http://localhost:5000/api';

// Search for articles
export const searchArticles = async (query, page = 1, limit = 5) => {
  const response = await axios.post(`${API_BASE_URL}/retrieve`, {
    query,
    page,
    limit,
  });
  return response.data;
};

// Summarize an article
export const summarizeArticle = async (articleId) => {
  const response = await axios.post(`${API_BASE_URL}/summarize`, {
    article_id: articleId,
  });
  return response.data;
};
