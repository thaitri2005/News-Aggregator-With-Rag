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
            primary: { main: '#90caf9' },
            secondary: { main: '#f48fb1' },
            background: { default: '#0f1115', paper: '#12161c' },
            text: { primary: '#e6e8eb', secondary: '#b0b3b8' },
          }
        : {
            mode: 'light',
            primary: { main: '#1a73e8' },
            secondary: { main: '#ff6f61' },
            background: { default: '#f6f8fb', paper: '#ffffff' },
            text: { primary: '#1f2937', secondary: '#6b7280' },
          },
      typography: {
        fontFamily: 'Poppins, Arial, sans-serif',
        h3: { fontWeight: 800 },
        h6: { fontWeight: 700 },
        body1: { lineHeight: 1.7 },
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
