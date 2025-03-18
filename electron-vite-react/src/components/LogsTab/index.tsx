import React, { useState } from 'react';
import { Box, Typography, Paper, Button } from '@mui/material';

const LogsTab: React.FC = () => {
  const [logs, setLogs] = useState<string[]>([]);

  const handleClearLogs = () => {
    setLogs([]);
  };

  const handleCopyLogs = () => {
    const logsText = logs.join('\n');
    navigator.clipboard.writeText(logsText);
  };

  return (
    <Box sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">Logs</Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button variant="outlined" onClick={handleCopyLogs}>Copy Logs</Button>
          <Button variant="outlined" onClick={handleClearLogs}>Clear Logs</Button>
        </Box>
      </Box>
      <Paper
        sx={{
          p: 2,
          height: 'calc(100vh - 200px)',
          backgroundColor: '#f5f5f5',
          overflow: 'auto'
        }}
      >
        {logs.map((log, index) => (
          <Typography
            key={index}
            variant="body2"
            component="pre"
            sx={{
              m: 0,
              fontFamily: 'monospace',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-all'
            }}
          >
            {log}
          </Typography>
        ))}
        {logs.length === 0 && (
          <Typography variant="body2" sx={{ color: 'text.secondary', textAlign: 'center', mt: 2 }}>
            No logs available
          </Typography>
        )}
      </Paper>
    </Box>
  );
};

export default LogsTab;