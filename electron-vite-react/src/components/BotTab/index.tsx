import React, { useEffect } from 'react';
import { Box, Button, Typography, Paper, Grid } from '@mui/material';
import axios from 'axios';
import { ClientStatus, BotInfo } from '../../types/bot';

interface BotTabProps {
  clientStatus: ClientStatus;
  botInfo: BotInfo;
}

const BotTab: React.FC<BotTabProps> = ({ clientStatus, botInfo }) => {

  const handleStartStop = async () => {
    try {
      if (!botInfo.isRunning) {
        await axios.post('http://localhost:5000/api/start_bot');
      } else {
        await axios.post('http://localhost:5000/api/stop_bot');
      }
    } catch (error) {
      console.error('Error starting/stopping bot:', error);
    }
  };


  const handleRestartUX = async () => {
    try {
      await axios.post('http://localhost:5000/api/restart_ux');
    } catch (error) {
      console.error('Error restarting UX:', error);
    }
  };

  const handleCloseClient = async () => {
    try {
      await axios.post('http://localhost:5000/api/close_client');
    } catch (error) {
      console.error('Error closing client:', error);
    }
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', color: '#1976d2' }}>Bot Control Panel</Typography>
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item>
          <Button 
            variant="contained" 
            onClick={handleStartStop}
            color={botInfo.isRunning ? 'error' : 'success'}
            size="large"
            sx={{ fontWeight: 'bold', minWidth: '120px' }}
          >
            {botInfo.isRunning ? 'Stop Bot' : 'Start Bot'}
          </Button>
        </Grid>
        <Grid item>
          <Button variant="outlined" onClick={handleRestartUX}>Restart UX</Button>
        </Grid>
        <Grid item>
          <Button variant="outlined" onClick={handleCloseClient}>Close Client</Button>
        </Grid>
      </Grid>

      <Grid container spacing={3} sx={{ display: 'flex', alignItems: 'stretch' }}>
        <Grid item xs={6} sx={{ display: 'flex' }}>
          <Paper sx={{ p: 3, borderRadius: 2, boxShadow: 3, width: '100%', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom sx={{ color: '#1976d2' }}>Game Status</Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">Current Phase</Typography>
                <Typography variant="h6" sx={{ fontWeight: 'medium' }}>{clientStatus.phase || 'N/A'}</Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">Account</Typography>
                <Typography variant="body1" sx={{ fontWeight: 'medium' }}>{clientStatus.summonerName || 'Not Connected'}</Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">Level</Typography>
                <Typography variant="body1">{clientStatus.summonerLevel || '0'}</Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={6} sx={{ display: 'flex' }}>
          <Paper sx={{ p: 3, borderRadius: 2, boxShadow: 3, width: '100%', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom sx={{ color: '#1976d2' }}>Bot Status</Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">Status</Typography>
                <Typography variant="h6" sx={{ 
                  fontWeight: 'medium',
                  color: botInfo.status === 'Error' ? 'error.main' : 'success.main'
                }}>
                  {botInfo.status || 'Inactive'}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 4 }}>
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">Runtime</Typography>
                  <Typography variant="body1">{botInfo.runTime || '0:00:00'}</Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">Games</Typography>
                  <Typography variant="body1">{botInfo.games}</Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">Errors</Typography>
                  <Typography variant="body1" color={botInfo.errors > 0 ? 'error.main' : 'text.primary'}>
                    {botInfo.errors}
                  </Typography>
                </Box>
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom sx={{ color: '#1976d2' }}>Output Log</Typography>
        <Paper 
          sx={{ 
            p: 2, 
            maxHeight: 200, 
            overflow: 'auto',
            backgroundColor: '#f8f9fa',
            borderRadius: 2
          }}
        >
          {botInfo.logs.split('\n').map((line, index) => (
            <Typography key={index} variant="body2" component="pre" sx={{ m: 0, fontFamily: '"Roboto Mono", monospace' }}>
              {line}
            </Typography>
          ))}
          {!botInfo.logs && (
            <Typography variant="body2" sx={{ color: 'text.secondary', textAlign: 'center', py: 2 }}>
              No output available
            </Typography>
          )}
        </Paper>
      </Box>
    </Box>
  );
};

export default BotTab;