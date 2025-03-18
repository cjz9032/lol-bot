import React, { useState } from 'react';
import { Box, Button, Typography, Paper, TextField, List, ListItem, ListItemText, ListItemSecondaryAction, IconButton } from '@mui/material';

interface Account {
  username: string;
  password: string;
}

const AccountsTab: React.FC = () => {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleAddAccount = () => {
    if (username && password) {
      setAccounts([...accounts, { username, password }]);
      setUsername('');
      setPassword('');
    }
  };

  const handleDeleteAccount = (index: number) => {
    const newAccounts = accounts.filter((_, i) => i !== index);
    setAccounts(newAccounts);
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>Add Account</Typography>
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
          <TextField
            label="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            size="small"
          />
          <TextField
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            size="small"
          />
          <Button
            variant="contained"
            onClick={handleAddAccount}
            disabled={!username || !password}
          >
            Add Account
          </Button>
        </Box>
      </Paper>

      <Typography variant="h6" gutterBottom>Accounts List</Typography>
      <Paper>
        <List>
          {accounts.map((account, index) => (
            <ListItem key={index}>
              <ListItemText
                primary={account.username}
                secondary="●●●●●●●●"
              />
              <ListItemSecondaryAction>
                <IconButton
                  edge="end"
                  onClick={() => handleDeleteAccount(index)}
                  color="error"
                >
                  ×
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  );
};

export default AccountsTab;