// frontend/src/components/SummaryPanel.js
import React from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Typography, Divider } from '@mui/material';

const SummaryPanel = ({ open, selectedArticle, onClose }) => {
  const title = selectedArticle?.title || 'Tóm tắt bài viết';
  const summary = selectedArticle?.summary || 'Chưa có tóm tắt.';

  return (
    <Dialog
      open={open}
      onClose={onClose}
      aria-labelledby="summary-dialog-title"
      fullWidth
      maxWidth="md"
      PaperProps={{
        sx: {
          borderRadius: 3,
          backdropFilter: 'blur(6px)',
          boxShadow: '0 12px 32px rgba(26,115,232,0.25)'
        }
      }}
    >
      <DialogTitle id="summary-dialog-title" sx={{ fontWeight: 700 }}>
        {title}
      </DialogTitle>
      <Divider />
      <DialogContent>
        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>
          {summary}
        </Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} variant="contained" sx={{ borderRadius: 2 }}>
          Đóng
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default SummaryPanel;
