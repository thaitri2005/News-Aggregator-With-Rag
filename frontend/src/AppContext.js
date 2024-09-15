import React, { createContext, useContext, useReducer } from 'react';
import axios from 'axios';

// Initial state
const initialState = {
  searchQuery: '',
  articles: [],
  selectedArticle: null,
  summaryPanelOpen: false,
  loading: false,
  error: null,
  page: 1,
  hasMore: true, // Track if there are more articles to load
};

// Reducer function to manage state
const reducer = (state, action) => {
  switch (action.type) {
    case 'SET_QUERY':
      return { 
        ...state, 
        searchQuery: action.payload, 
        page: 1, 
        articles: [], // Reset articles on new search
        hasMore: true, // Reset hasMore when new search is triggered
      };
    case 'SET_ARTICLES':
      return { 
        ...state, 
        articles: [...state.articles, ...action.payload], // Append new articles
        page: state.page + 1,  // Increment page
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
  const searchArticles = async (query, page = 1) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    dispatch({ type: 'SET_ERROR', payload: null });

    try {
      const response = await axios.post('http://localhost:5000/api/retrieve', {
        query,
        page,
        limit: 5,
      });

      dispatch({ type: 'SET_ARTICLES', payload: response.data });
      
      // Check if there are more articles to load
      dispatch({ type: 'SET_HAS_MORE', payload: response.data.length > 0 });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: 'An error occurred while fetching the articles' });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  // Function to load more articles (for lazy loading)
  const loadMoreArticles = async (query, page) => {
    if (!state.hasMore || state.loading) return; // Prevent duplicate loading
    searchArticles(query, page);
  };

  // Function to fetch summary of an article
  const fetchSummary = async (article) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      const response = await axios.post('http://localhost:5000/api/summarize', {
        article_text: article.content,
      });
      dispatch({
        type: 'SET_SELECTED_ARTICLE',
        payload: { ...article, summary: response.data.summary || 'No summary available' },
      });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: 'Failed to load summary' });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  return (
    <AppContext.Provider value={{ state, dispatch, searchArticles, fetchSummary, loadMoreArticles }}>
      {children}
    </AppContext.Provider>
  );
};

// Hook to use context
export const useAppContext = () => useContext(AppContext);
