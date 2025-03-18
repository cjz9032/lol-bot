import React, { useState } from 'react';
import { Box, Typography, Paper, TextField, Button, Select, MenuItem, FormControl, InputLabel, Grid } from '@mui/material';

interface HTTPResponse {
  status: number;
  data: any;
}

const HTTPTab: React.FC = () => {
  const [method, setMethod] = useState('GET');
  const [url, setUrl] = useState('');
  const [body, setBody] = useState('');
  const [response, setResponse] = useState<HTTPResponse | null>(null);

  const handleSendRequest = async () => {
    // TODO: Implement actual HTTP request logic
    console.log('Sending request:', { method, url, body });
  };

  const handleFormatJSON = () => {
    try {
      const formatted = JSON.stringify(JSON.parse(body), null, 2);
      setBody(formatted);
    } catch (error) {
      console.error('Invalid JSON:', error);
    }
  };

  const handleCopyToClipboard = () => {
    if (response) {
      navigator.clipboard.writeText(JSON.stringify(response.data, null, 2));
    }
  };

  return (
    <Box sx={{ p: 2 }}>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <FormControl fullWidth>
            <InputLabel>Method</InputLabel>
            <Select
              value={method}
              label="Method"
              onChange={(e) => setMethod(e.target.value)}
            >
              <MenuItem value="GET">GET</MenuItem>
              <MenuItem value="POST">POST</MenuItem>
              <MenuItem value="PUT">PUT</MenuItem>
              <MenuItem value="PATCH">PATCH</MenuItem>
              <MenuItem value="DELETE">DELETE</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12}>
          <TextField
            fullWidth
            label="URL"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Enter request URL"
          />
        </Grid>

        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Body"
            multiline
            rows={4}
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="Enter request body (JSON)"
          />
        </Grid>

        <Grid item xs={12}>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button variant="contained" onClick={handleSendRequest}>Send Request</Button>
            <Button variant="outlined" onClick={handleFormatJSON}>Format JSON</Button>
          </Box>
        </Grid>

        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>Response</Typography>
          <Paper sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
            {response && (
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography>Status: {response.status}</Typography>
                  <Button size="small" onClick={handleCopyToClipboard}>Copy to Clipboard</Button>
                </Box>
                <TextField
                  fullWidth
                  multiline
                  rows={6}
                  value={JSON.stringify(response.data, null, 2)}
                  InputProps={{ readOnly: true }}
                />
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default HTTPTab;