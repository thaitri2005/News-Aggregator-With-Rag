// frontend/src/services/api.js
import axios from 'axios';

// API base URL
const API_BASE_URL = 'http://localhost:5000/api';

/**
 * Search for articles with advanced options like sorting and pagination.
 *
 * @param {string} query - The search query string.
 * @param {number} page - The page number for pagination (default: 1).
 * @param {number} limit - The number of articles per page (default: 5).
 * @param {string} sort_by - The field to sort by ('score' or 'date', default: 'score').
 * @param {string} order - The sort order ('asc' or 'desc', default: 'desc').
 * @returns {Promise<Array>} - A promise that resolves to an array of articles.
 * @throws {Error} - Throws an error if the request fails.
 */
export const searchArticles = async (
  query,
  page = 1,
  limit = 5,
  sort_by = 'score',
  order = 'desc'
) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/retrieve`, {
      query,
      page,
      limit,
      sort_by,
      order,
    });

    // Debug: Log the successful response
    console.log('API Search Response:', response.data);

    // Ensure the response is an array of articles
    if (Array.isArray(response.data)) {
      return response.data;
    } else {
      // If the response contains a message (e.g., no articles found), return an empty array
      return [];
    }
  } catch (error) {
    // Handle different error scenarios
    if (error.response) {
      // Server responded with a status other than 2xx
      if (error.response.status === 404) {
        // No articles found matching the query
        console.warn('No articles found for the given query.');
        return []; // Return an empty array to indicate no results
      } else {
        // Other server-side errors
        console.error('API Error:', error.response.data);
        throw new Error(
          error.response.data.description ||
            'An error occurred while fetching the articles.'
        );
      }
    } else if (error.request) {
      // Request was made but no response received
      console.error('No response received from the server.');
      throw new Error('No response received from the server.');
    } else {
      // Something happened while setting up the request
      console.error('Error setting up the request:', error.message);
      throw new Error('Error setting up the request.');
    }
  }
};

/**
 * Fetch the summary of a specific article.
 *
 * @param {string} articleId - The unique identifier of the article.
 * @returns {Promise<Object>} - A promise that resolves to an object containing the summary.
 * @throws {Error} - Throws an error if the request fails.
 */
export const summarizeArticle = async (articleId) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/summarize`, {
      article_id: articleId,
    });

    // Debug: Log the successful response
    console.log('API Summarize Response:', response.data);

    // Ensure the response contains the summary
    if (response.data && response.data.summary) {
      return response.data;
    } else {
      // If the summary is missing, return a default message
      return { summary: 'No summary available.' };
    }
  } catch (error) {
    // Handle different error scenarios
    if (error.response) {
      // Server responded with a status other than 2xx
      if (error.response.status === 404) {
        // Article not found
        console.warn('Article not found for summarization.');
        throw new Error('Article not found.');
      } else {
        // Other server-side errors
        console.error('API Error:', error.response.data);
        throw new Error(
          error.response.data.description ||
            'An error occurred while summarizing the article.'
        );
      }
    } else if (error.request) {
      // Request was made but no response received
      console.error('No response received from the server.');
      throw new Error('No response received from the server.');
    } else {
      // Something happened while setting up the request
      console.error('Error setting up the request:', error.message);
      throw new Error('Error setting up the request.');
    }
  }
};
