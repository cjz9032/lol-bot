export interface ClientStatus {
  phase: string;
  summonerName: string;
  summonerLevel: number;
  gameTime: string;
  champion: string;
}

export interface BotInfo {
  status: string;
  runTime: string;
  games: number;
  errors: number;
  logs: string;
  isRunning: boolean;
}