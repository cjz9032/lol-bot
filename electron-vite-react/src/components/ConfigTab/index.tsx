import React, { useState } from 'react';
import { Box, Typography, Paper, TextField, Button, Grid, Switch, FormControlLabel } from '@mui/material';

interface Config {
  windowsInstallDir: string;
  macosInstallDir: string;
  autoAcceptQueue: boolean;
  autoHonorTeammate: boolean;
}

const ConfigTab: React.FC = () => {
  const [config, setConfig] = useState<Config>({
    windowsInstallDir: '',
    macosInstallDir: '',
    autoAcceptQueue: true,
    autoHonorTeammate: true
  });

  const handleSave = () => {
    // TODO: Implement save configuration logic
    console.log('Saving config:', config);
  };

  const handleChange = (key: keyof Config) => (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.type === 'checkbox' ? event.target.checked : event.target.value;
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>Configuration Settings</Typography>
      <Paper sx={{ p: 2 }}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Windows Install Directory"
              value={config.windowsInstallDir}
              onChange={handleChange('windowsInstallDir')}
              helperText="Path to League of Legends installation on Windows"
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="macOS Install Directory"
              value={config.macosInstallDir}
              onChange={handleChange('macosInstallDir')}
              helperText="Path to League of Legends installation on macOS"
            />
          </Grid>
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={config.autoAcceptQueue}
                  onChange={handleChange('autoAcceptQueue')}
                />
              }
              label="Auto Accept Queue"
            />
          </Grid>
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={config.autoHonorTeammate}
                  onChange={handleChange('autoHonorTeammate')}
                />
              }
              label="Auto Honor Teammate"
            />
          </Grid>
          <Grid item xs={12}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleSave}
            >
              Save Configuration
            </Button>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default ConfigTab;