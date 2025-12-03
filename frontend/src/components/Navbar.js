import React from 'react';
import { AppBar, Toolbar, Typography, IconButton, Box } from '@mui/material';
import NewspaperIcon from '@mui/icons-material/Newspaper';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import { useThemeContext } from '../contexts/ThemeContext';

const Navbar = () => {
  const { darkMode, toggleDarkMode } = useThemeContext();

  return (
    <AppBar 
      position="sticky" 
      elevation={0}
      sx={{
        background: (theme) => theme.palette.background.paper,
        borderBottom: (theme) => theme.palette.mode === 'dark' ? '1px solid #2a2a2a' : '1px solid #e5e7eb',
        backdropFilter: 'blur(10px)',
      }}
    >
      <Toolbar sx={{ py: 1 }}>
        <NewspaperIcon sx={{ fontSize: 28, mr: 2 }} />
        <Typography 
          variant="h6" 
          sx={{ 
            flexGrow: 1, 
            fontWeight: 700, 
            letterSpacing: -0.5,
            fontSize: '1.3rem'
          }}
        >
          News Aggregator
        </Typography>
        <Box>
          <IconButton 
            onClick={toggleDarkMode} 
            sx={{
              border: (theme) => theme.palette.mode === 'dark' ? '1px solid #2a2a2a' : '1px solid #e5e7eb',
              borderRadius: 1.5,
              '&:hover': {
                background: (theme) => theme.palette.mode === 'dark' ? '#1a1a1a' : '#f3f4f6'
              }
            }}
          >
            {darkMode ? <Brightness7Icon fontSize="small" /> : <Brightness4Icon fontSize="small" />}
          </IconButton>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
