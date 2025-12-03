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
          borderRadius: 2,
          border: (theme) => theme.palette.mode === 'dark' ? '1px solid #2a2a2a' : '1px solid #e5e7eb',
        }
      }}
    >
      <DialogTitle id="summary-dialog-title" sx={{ fontWeight: 700, pb: 2 }}>
        {title}
      </DialogTitle>
      <Divider sx={{ opacity: 0.6 }} />
      <DialogContent sx={{ pt: 3, pb: 3 }}>
        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>
          {summary}
        </Typography>
      </DialogContent>
      <Divider sx={{ opacity: 0.6 }} />
      <DialogActions sx={{ p: 2.5 }}>
        <Button 
          onClick={onClose} 
          variant="outlined"
          sx={{ 
            borderRadius: 1.5,
            px: 3,
            borderColor: (theme) => theme.palette.mode === 'dark' ? '#3a3a3a' : '#e5e7eb',
            '&:hover': {
              borderColor: (theme) => theme.palette.mode === 'dark' ? '#ffffff' : '#000000',
              background: 'transparent'
            }
          }}
        >
          Đóng
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default SummaryPanel;
