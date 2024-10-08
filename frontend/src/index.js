// frontend/src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import { AppProvider } from './contexts/AppContext'; // Importing the context provider
import reportWebVitals from './reportWebVitals'; // Importing web vitals reporting
import { ThemeProvider } from './contexts/ThemeContext';

// Create root for rendering the app
const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    <ThemeProvider>
      <AppProvider>
        <App />
      </AppProvider>
    </ThemeProvider>
  </React.StrictMode>
);

// Web Vitals for performance measurement
reportWebVitals();
