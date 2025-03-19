import React, { useState, useEffect } from 'react';
import { Box, Tabs, Tab } from '@mui/material';
import axios from 'axios';
import { ClientStatus, BotInfo } from './types/bot';
import { useRequest } from 'ahooks';

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
  const [clientStatus, setClientStatus] = useState<ClientStatus>({    
    phase: "",
    summonerName: "",
    summonerLevel: 0,
    champion: "",
    gameTime: ""
  });
  const [botInfo, setBotInfo] = useState<BotInfo>({    
    status: "",
    runTime: "",
    games: 0,
    errors: 0,
    logs: "",
    isRunning: false
  });

  const { data, run } = useRequest(
    async () => {
      const response = await axios.get('http://localhost:5000/api/status');
      return response.data;
    },
    {
      pollingInterval: 1000,
      pollingWhenHidden: false,
      refreshOnWindowFocus: false,
      onSuccess: (data) => {
        setClientStatus(data);
        setBotInfo({
          status: data.status,
          runTime: data.runTime,
          games: data.games,
          errors: data.errors,
          logs: data.phase,
          isRunning: data.isRunning
        });
      },
      onError: (error) => {
        console.error('Error fetching status:', error);
      }
    }
  );

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  return (
    <Box>
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
        <BotTab clientStatus={clientStatus} botInfo={botInfo} />
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