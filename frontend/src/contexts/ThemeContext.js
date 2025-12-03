// frontend/src/contexts/ThemeContext.js
import React, { createContext, useState, useContext, useMemo } from 'react';
import { ThemeProvider as MUIThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

const ThemeContext = createContext();
export const useThemeContext = () => useContext(ThemeContext);

export const ThemeProvider = ({ children }) => {
  const [darkMode, setDarkMode] = useState(false);

  const toggleDarkMode = () => setDarkMode((prev) => !prev);

  const theme = useMemo(() =>
    createTheme({
      palette: darkMode
        ? {
            mode: 'dark',
            primary: { main: '#ffffff' },
            secondary: { main: '#9ca3af' },
            background: { default: '#0a0a0a', paper: '#141414' },
            text: { primary: '#f9fafb', secondary: '#9ca3af' },
          }
        : {
            mode: 'light',
            primary: { main: '#000000' },
            secondary: { main: '#6b7280' },
            background: { default: '#f9fafb', paper: '#ffffff' },
            text: { primary: '#111827', secondary: '#6b7280' },
          },
      typography: {
        fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        h3: { fontWeight: 800, letterSpacing: -1.5 },
        h6: { fontWeight: 700 },
        body1: { lineHeight: 1.7 },
        button: { textTransform: 'none', fontWeight: 600 },
      },
      shape: { borderRadius: 12 },
    }),
    [darkMode]
  );

  return (
    <ThemeContext.Provider value={{ darkMode, toggleDarkMode }}>
      <MUIThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </MUIThemeProvider>
    </ThemeContext.Provider>
  );
};
