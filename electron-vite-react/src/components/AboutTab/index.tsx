import React from 'react';
import { Box, Typography, Paper, Link } from '@mui/material';

const AboutTab: React.FC = () => {
  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>About LoL Bot</Typography>
      <Paper sx={{ p: 2 }}>
        <Typography variant="body1" paragraph>
          LoL Bot is an automated League of Legends client that helps you manage and automate various game-related tasks.
        </Typography>
        
        <Typography variant="subtitle1" gutterBottom>Features</Typography>
        <Typography component="ul" sx={{ pl: 2 }}>
          <li>Automated game client management</li>
          <li>Account management system</li>
          <li>Configurable bot settings</li>
          <li>Custom HTTP requests to League Client API</li>
          <li>Detailed logging system</li>
        </Typography>

        <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>Links</Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Link href="https://github.com/your-repo/lol-bot" target="_blank" rel="noopener">
            GitHub Repository
          </Link>
          <Link href="https://developer.riotgames.com/" target="_blank" rel="noopener">
            Riot Games API
          </Link>
        </Box>

        <Typography variant="body2" sx={{ mt: 2, color: 'text.secondary' }}>
          Version: 1.0.0
        </Typography>
      </Paper>
    </Box>
  );
};

export default AboutTab;