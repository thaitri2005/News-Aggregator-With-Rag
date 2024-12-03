// frontend/src/contexts/AppContext.js
import React, { createContext, useContext, useReducer } from 'react';
import { searchArticles, summarizeArticle } from '../services/api';

// Initial state
const initialState = {
  searchQuery: '',
  articles: [],
  selectedArticle: null,
  summaryPanelOpen: false,
  loading: false,
  error: null,
  page: 1,
  hasMore: true,
  sort_by: 'score',
  order: 'desc',
  sources: ['VNExpress', 'Tuổi Trẻ', 'VietnamNet', 'Thanh Niên', 'Dân Trí'], // Default sources
};

// Reducer function to manage state
const reducer = (state, action) => {
  switch (action.type) {
    case 'SET_QUERY':
      return { 
        ...state, 
        searchQuery: action.payload, 
        page: 1, 
        articles: [], 
        hasMore: true, 
      };
    case 'SET_ARTICLES':
      return { 
        ...state, 
        articles: [...state.articles, ...action.payload], 
        page: state.page + 1, 
      };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'SET_HAS_MORE':
      return { ...state, hasMore: action.payload };
    case 'SET_SELECTED_ARTICLE':
      return { ...state, selectedArticle: action.payload, summaryPanelOpen: true };
    case 'CLOSE_SUMMARY_PANEL':
      return { ...state, selectedArticle: null, summaryPanelOpen: false };
    case 'SET_SOURCES':
      return { ...state, sources: action.payload };
    default:
      return state;
  }
};

// Create context
const AppContext = createContext();

// Context provider
export const AppProvider = ({ children }) => {
  const [state, dispatch] = useReducer(reducer, initialState);

  // Function to search articles
  const searchArticlesWithOptions = async (
    query, 
    page = 1, 
    limit = 5, 
    sort_by = 'score', 
    order = 'desc', 
    sources = []
  ) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    dispatch({ type: 'SET_ERROR', payload: null });

    try {
      const filters = { sources };
      const response = await searchArticles(query, page, limit, sort_by, order, filters);
      
      // Debug: Log the response
      console.log('Articles fetched:', response);

      dispatch({ type: 'SET_ARTICLES', payload: response });

      // Check if there are more articles to load
      dispatch({ type: 'SET_HAS_MORE', payload: response.length > 0 });
    } catch (error) {
      console.error('Error fetching articles:', error.message);
      dispatch({ type: 'SET_ERROR', payload: error.message });
      dispatch({ type: 'SET_HAS_MORE', payload: false });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  // Function to load more articles (for lazy loading)
  const loadMoreArticles = async (
    query, 
    page, 
    limit = 5, 
    sort_by = 'score', 
    order = 'desc', 
    sources = []
  ) => {
    if (!state.hasMore || state.loading) return; // Prevent duplicate loading
    await searchArticlesWithOptions(query, page, limit, sort_by, order, sources);
  };

  // Function to fetch article summaries
  const fetchSummary = async (article) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    dispatch({ type: 'SET_ERROR', payload: null });
  
    try {
      // Log the article ID being sent for summarization
      console.log('Sending article_id:', article.id || article._id);
  
      // Send the article ID to the summarize API
      const response = await summarizeArticle(article.id || article._id);
  
      // Debug: Log the response from the backend
      console.log('Summary API response:', response);
  
      // Update the selected article in the state
      dispatch({
        type: 'SET_SELECTED_ARTICLE',
        payload: { ...article, summary: response.summary || 'No summary available.' },
      });
    } catch (error) {
      console.error('Error fetching summary:', error.message);
      dispatch({ type: 'SET_ERROR', payload: error.message });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };  

  return (
    <AppContext.Provider value={{ state, dispatch, searchArticlesWithOptions, fetchSummary, loadMoreArticles }}>
      {children}
    </AppContext.Provider>
  );
};

// Hook to use context
export const useAppContext = () => useContext(AppContext);
