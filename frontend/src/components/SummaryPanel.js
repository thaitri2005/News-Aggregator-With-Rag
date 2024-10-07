// frontend/src/components/SummaryPanel.js
import React from 'react';
import { Box, Typography, Button } from '@mui/material';

const SummaryPanel = ({ selectedArticle, dispatch }) => (
  <Box className="summary-panel" role="complementary" aria-label="Summary panel">
    <Button onClick={() => dispatch({ type: 'CLOSE_SUMMARY_PANEL' })}>Close</Button>
    <Typography variant="h6">{selectedArticle.title}</Typography>
    <Typography variant="body1">{selectedArticle.summary}</Typography>
  </Box>
);

export default SummaryPanel;
