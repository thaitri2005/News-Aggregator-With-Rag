// frontend/src/components/SearchBar.js
import React from 'react';
import { TextField, Button, CircularProgress } from '@mui/material';

const SearchBar = ({ searchQuery, handleSearchInput, handleKeyDown, handleSearch, loading }) => (
  <div className="search-container">
    <TextField
      value={searchQuery}
      onChange={handleSearchInput}
      variant="outlined"
      placeholder="Search for news articles..."
      onKeyDown={handleKeyDown}
      className="search-input"
    />
    <Button
      onClick={handleSearch}
      variant="contained"
      color="primary"
      className="search-button"
      disabled={loading}
    >
      {loading ? <CircularProgress size={24} color="inherit" /> : 'Search'}
    </Button>
  </div>
);

export default SearchBar;
