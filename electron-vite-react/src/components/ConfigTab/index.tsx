import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, TextField, Button, Grid, Switch, FormControlLabel, Select, MenuItem, FormControl, InputLabel, CircularProgress, Backdrop } from '@mui/material';
import axios from 'axios';

interface Config {
  windows_install_dir: string;
  macos_install_dir: string;
  lobby: number;
  max_level: number;
  fps_type: number;
  cjk_support: boolean;
  font_scale: number;
}

const ALL_LOBBIES = {
  'Draft Pick': 400,
  'Ranked Solo/Duo': 420,
  'Blind Pick': 430,
  'Ranked Flex': 440,
  'ARAM': 450,
  'Intro Bots': 870,
  'Beginner Bots': 880,
  'Intermediate Bots': 890,
  'Normal TFT': 1090,
  'Ranked TFT': 1100,
  'Hyper Roll TFT': 1130,
  'Double Up TFT': 1160
};

const BOT_LOBBIES = {
  'Intro Bots': 870,
  'Beginner Bots': 880,
  'Intermediate Bots': 890,
}

const FPS_OPTIONS = {
  '25': 3,
  '30': 4,
  '60': 5,
  '80': 6,
  '120': 7,
  '144': 8,
  '200': 9,
  '240': 2,
  'Uncapped': 10
};

const ConfigTab: React.FC = () => {
  const [config, setConfig] = useState<Config>({
    windows_install_dir: 'C:/Riot Games/League of Legends',
    macos_install_dir: '/Applications/League of Legends.app',
    lobby: 880,
    max_level: 30,
    fps_type: 5,
    cjk_support: false,
    font_scale: 0.7
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:5000/api/config');
      setConfig(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load configuration');
      console.error('Error loading config:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      await axios.post('http://localhost:5000/api/config', config);
      setError(null);
    } catch (err) {
      setError('Failed to save configuration');
      console.error('Error saving config:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 2 }}>
      <Paper sx={{ p: 3, position: 'relative' }}>
        <Typography variant="h6" gutterBottom>Configuration Settings</Typography>
        {error && (
          <Typography color="error" sx={{ mb: 2 }}>{error}</Typography>
        )}
        <Backdrop
          sx={{
            position: 'absolute',
            color: '#fff',
            zIndex: (theme) => theme.zIndex.drawer + 1,
            backgroundColor: 'rgba(0, 0, 0, 0.3)'
          }}
          open={loading}
        >
          <CircularProgress color="inherit" />
        </Backdrop>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Windows Install Directory"
              value={config.windows_install_dir}
              onChange={(e) => setConfig({ ...config, windows_install_dir: e.target.value })}
              disabled={loading}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="macOS Install Directory"
              value={config.macos_install_dir}
              onChange={(e) => setConfig({ ...config, macos_install_dir: e.target.value })}
              disabled={loading}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Game Mode</InputLabel>
              <Select
                value={config.lobby}
                label="Game Mode"
                onChange={(e) => setConfig({ ...config, lobby: Number(e.target.value) })}
                disabled={loading}
              >
                {Object.entries(BOT_LOBBIES).map(([name, id]) => (
                  <MenuItem key={id} value={id}>{name}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              type="number"
              label="Max Level"
              value={config.max_level}
              onChange={(e) => setConfig({ ...config, max_level: Number(e.target.value) })}
              inputProps={{ min: 1, max: 500 }}
              disabled={loading}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>FPS Setting</InputLabel>
              <Select
                value={config.fps_type}
                label="FPS Setting"
                onChange={(e) => setConfig({ ...config, fps_type: Number(e.target.value) })}
                disabled={loading}
              >
                {Object.entries(FPS_OPTIONS).map(([fps, value]) => (
                  <MenuItem key={value} value={value}>{fps} FPS</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              type="number"
              label="Font Scale"
              value={config.font_scale}
              onChange={(e) => setConfig({ ...config, font_scale: Number(e.target.value) })}
              inputProps={{ min: 0.1, max: 2, step: 0.1 }}
              disabled={loading}
            />
          </Grid>
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={config.cjk_support}
                  onChange={(e) => setConfig({ ...config, cjk_support: e.target.checked })}
                  disabled={loading}
                />
              }
              label="CJK Font Support"
            />
          </Grid>
          <Grid item xs={12}>
            <Button
              variant="contained"
              onClick={handleSave}
              disabled={loading}
            >
              {loading ? 'Saving...' : 'Save Configuration'}
            </Button>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default ConfigTab;