// frontend/src/contexts/ThemeContext.js
import React, { createContext, useState, useContext } from 'react';

// Create a ThemeContext
const ThemeContext = createContext();

// Create a custom hook to use the ThemeContext
export const useThemeContext = () => useContext(ThemeContext);

// Create a provider component
export const ThemeProvider = ({ children }) => {
  const [darkMode, setDarkMode] = useState(false);

  const toggleDarkMode = () => {
    setDarkMode((prevMode) => !prevMode);
  };

  return (
    <ThemeContext.Provider value={{ darkMode, toggleDarkMode }}>
      {children}
    </ThemeContext.Provider>
  );
};
