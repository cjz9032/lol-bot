/**
 * Handles all HTTP requests to the local game server,
 * providing functions for interacting with various game endpoints.
 */

import fetch from 'node-fetch';
import https from 'https';

const httpsAgent = new https.Agent({
  rejectUnauthorized: false,
});
const GAME_SERVER_URL = 'https://127.0.0.1:2999/liveclientdata/allgamedata';

export class GameServerError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'GameServerError';
  }
}

export class GameServer {
  private data: string | null = null;

  private async updateData(): Promise<void> {
    try {
      const response = await fetch(GAME_SERVER_URL, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        },
        signal: AbortSignal.timeout(20000),
        agent: httpsAgent,
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      this.data = await response.text();
    } catch (e) {
      throw new GameServerError(`Failed to get game data: ${e}`);
    }
  }

  async isRunning(): Promise<boolean> {
    try {
      await this.updateData();
      return true;
    } catch (GameServerError) {
      return false;
    }
  }

  async getGameTime(): Promise<number> {
    try {
      await this.updateData();
      const data = JSON.parse(this.data!);
      return parseInt(data.gameData.gameTime);
    } catch (e) {
      throw new GameServerError(`Failed to get game time: ${e}`);
    }
  }

  async getFormattedTime(): Promise<string> {
    try {
      await this.updateData();
      const seconds = await this.getGameTime();
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = Math.floor(seconds % 60);
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    } catch (GameServerError) {
      return 'XX:XX';
    }
  }

  async getChamp(): Promise<string> {
    try {
      await this.updateData();
      const data = JSON.parse(this.data!);
      for (const player of data.allPlayers) {
        if (player.summonerName === data.activePlayer.summonerName) {
          return player.championName;
        }
      }
      return '';
    } catch (e) {
      throw new GameServerError(`Failed to get champion information: ${e}`);
    }
  }

  async summonerIsDead(): Promise<boolean> {
    try {
      await this.updateData();
      const data = JSON.parse(this.data!);
      for (const player of data.allPlayers) {
        if (player.summonerName === data.activePlayer.summonerName) {
          return Boolean(player.isDead);
        }
      }
      return false;
    } catch (e) {
      throw new GameServerError(`Failed to get champion alive status: ${e}`);
    }
  }

  async getSummonerHealth(): Promise<number> {
    try {
      await this.updateData();
      const data = JSON.parse(this.data!);
      const currentHealth = parseFloat(data.activePlayer.championStats.currentHealth);
      const maxHealth = parseFloat(data.activePlayer.championStats.maxHealth);
      return maxHealth > 0 ? currentHealth / maxHealth : 0;
    } catch (e) {
      throw new GameServerError(`Failed to get champion health status: ${e}`);
    }
  }

  async getSummonerGold(): Promise<number> {
    try {
      await this.updateData();
      const data = JSON.parse(this.data!);
      return parseInt(data.activePlayer.currentGold);
    } catch (e) {
      throw new GameServerError(`Failed to get champion gold: ${e}`);
    }
  }
}