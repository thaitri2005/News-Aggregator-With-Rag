import React from 'react';
import { AppBar, Toolbar, Typography, IconButton, Box } from '@mui/material';
import NewspaperIcon from '@mui/icons-material/Newspaper';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import { useThemeContext } from '../contexts/ThemeContext';

const Navbar = () => {
  const { darkMode, toggleDarkMode } = useThemeContext();

  return (
    <AppBar position="sticky" elevation={6} sx={{
      background: darkMode
        ? 'rgba(30, 30, 30, 0.95)'
        : 'linear-gradient(90deg, #1a73e8 0%, #2196f3 100%)',
      backdropFilter: 'blur(8px)',
      boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
    }}>
      <Toolbar>
        <NewspaperIcon sx={{ fontSize: 32, mr: 2, color: '#fff' }} />
        <Typography variant="h5" sx={{ flexGrow: 1, fontWeight: 700, letterSpacing: 1, color: '#fff' }}>
          News Aggregator
        </Typography>
        <Box>
          <IconButton onClick={toggleDarkMode} color="inherit">
            {darkMode ? <Brightness7Icon /> : <Brightness4Icon />}
          </IconButton>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
