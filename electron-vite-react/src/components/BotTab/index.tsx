import React from 'react';
import { Box, Button, Typography, Paper, Grid } from '@mui/material';

interface ClientStatus {
  phase: string;
  summoner_name: string;
  summoner_level: string;
}

interface BotTabProps {
  clientStatus: ClientStatus;
}

const BotTab: React.FC<BotTabProps> = ({ clientStatus }) => {
  const [isRunning, setIsRunning] = React.useState(false);
  const [output, setOutput] = React.useState<string[]>([]);
  const [botInfo, setBotInfo] = React.useState({
    status: 'Ready',
    runTime: '-',
    games: '-',
    errors: '-',
    action: '-'
  });

  const handleStartStop = () => {
    setIsRunning(!isRunning);
    // TODO: Implement actual bot start/stop logic
  };

  const handleClearOutput = () => {
    setOutput([]);
  };

  const handleRestartUX = () => {
    // TODO: Implement UX restart logic
  };

  const handleCloseClient = () => {
    // TODO: Implement client close logic
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>Controls</Typography>
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item>
          <Button 
            variant="contained" 
            onClick={handleStartStop}
            color={isRunning ? 'error' : 'primary'}
          >
            {isRunning ? 'Stop Bot' : 'Start Bot'}
          </Button>
        </Grid>
        <Grid item>
          <Button variant="contained" onClick={handleClearOutput}>Clear Output</Button>
        </Grid>
        <Grid item>
          <Button variant="contained" onClick={handleRestartUX}>Restart UX</Button>
        </Grid>
        <Grid item>
          <Button variant="contained" onClick={handleCloseClient}>Close Client</Button>
        </Grid>
      </Grid>

      <Grid container spacing={2}>
        <Grid item xs={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>Info</Typography>
            <Typography variant="body2">Phase: {clientStatus.phase}</Typography>
            <Typography variant="body2">Account: {clientStatus.summoner_name}</Typography>
            <Typography variant="body2">Level: {clientStatus.summoner_level}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>Bot</Typography>
            <Typography variant="body2">Status: {botInfo.status}</Typography>
            <Typography variant="body2">Runtime: {botInfo.runTime}</Typography>
            <Typography variant="body2">Games: {botInfo.games}</Typography>
            <Typography variant="body2">Errors: {botInfo.errors}</Typography>
            <Typography variant="body2">Action: {botInfo.action}</Typography>
          </Paper>
        </Grid>
      </Grid>

      <Box sx={{ mt: 3 }}>
        <Typography variant="h6" gutterBottom>Output</Typography>
        <Paper 
          sx={{ 
            p: 2, 
            maxHeight: 200, 
            overflow: 'auto',
            backgroundColor: '#f5f5f5'
          }}
        >
          {output.map((line, index) => (
            <Typography key={index} variant="body2" component="pre" sx={{ m: 0 }}>
              {line}
            </Typography>
          ))}
        </Paper>
      </Box>
    </Box>
  );
};

export default BotTab;