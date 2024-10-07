// frontend/src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import { AppProvider } from './contexts/AppContext'; // Importing the context provider
import reportWebVitals from './reportWebVitals'; // Importing web vitals reporting

// Create root for rendering the app
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    {/* Wrap the App with AppProvider to provide global state/context */}
    <AppProvider>
      <App />
    </AppProvider>
  </React.StrictMode>
);

// Web Vitals for performance measurement
reportWebVitals();
