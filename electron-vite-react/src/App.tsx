import React, { useState, useEffect } from 'react';
import { Box, Tabs, Tab } from '@mui/material';
import axios from 'axios';

// Import our tab components
import BotTab from './components/BotTab';
import AccountsTab from './components/AccountsTab';
import ConfigTab from './components/ConfigTab';
import HTTPTab from './components/HTTPTab';
import LogsTab from './components/LogsTab';
import AboutTab from './components/AboutTab';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function App() {
  const [value, setValue] = useState(0);
  const [clientStatus, setClientStatus] = useState({
    phase: 'None',
    summoner_name: '-',
    summoner_level: '-'
  });

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/status');
        setClientStatus(response.data);
      } catch (error) {
        console.error('Error fetching status:', error);
      }
    };

    const interval = setInterval(fetchStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={value} onChange={handleChange}>
          <Tab label="Bot" />
          <Tab label="Accounts" />
          <Tab label="Config" />
          <Tab label="HTTP" />
          <Tab label="Logs" />
          <Tab label="About" />
        </Tabs>
      </Box>
      <TabPanel value={value} index={0}>
        <BotTab clientStatus={clientStatus} />
      </TabPanel>
      <TabPanel value={value} index={1}>
        <AccountsTab />
      </TabPanel>
      <TabPanel value={value} index={2}>
        <ConfigTab />
      </TabPanel>
      <TabPanel value={value} index={3}>
        <HTTPTab />
      </TabPanel>
      <TabPanel value={value} index={4}>
        <LogsTab />
      </TabPanel>
      <TabPanel value={value} index={5}>
        <AboutTab />
      </TabPanel>
    </Box>
  );
}

export default App;