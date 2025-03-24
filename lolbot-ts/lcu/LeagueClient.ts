import axios, { AxiosInstance, AxiosResponse } from 'axios';
import https from 'https';

// Import system command utilities (assuming cmd is converted to TS)
import { cmd } from '../system/cmd';

// Interfaces for API responses
interface SummonerResponse {
    displayName?: string;
    gameName?: string;
    summonerLevel: number;
}

interface GamePhaseResponse {
    gameData: {
        gameTime: number;
    };
}

interface LobbyResponse {
    gameConfig: {
        queueId: number;
    };
}

interface ChampSelectSession {
    // Add champion select specific fields
    actions: any[];
    timer: {
        adjustedTimeLeftInPhase: number;
    };
}

interface MatchmakingSearch {
    errors: Array<{
        penaltyTimeRemaining: number;
    }>;
    estimatedQueueTime: number;
    timeInQueue: number;
}

/** Exception for LCU API errors */
export class LCUError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'LCUError';
    }
}

export class LeagueClient {
    private client: AxiosInstance;
    private timer: NodeJS.Timeout | null;
    private endpoint: string;

    constructor() {
        this.client = axios.create({
            httpsAgent: new (https.Agent)({ rejectUnauthorized: false }),
            headers: { 'Accept': 'application/json' },
            timeout: 15000,
        });
        this.timer = null;
        this.endpoint = cmd.getAuthString();
    }

    public updateAuth(): void {
        this.endpoint = cmd.getAuthString();
    }

    public updateAuthTimer(timer: number = 5): void {
        this.endpoint = cmd.getAuthString();
        this.timer = setInterval(() => this.updateAuthTimer(timer), timer * 1000);
    }

    public stopTimer(): void {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    }

    private async makeRequest<T>(method: string, url: string, body?: any): Promise<AxiosResponse<T>> {
        const fullUrl = `${this.endpoint}${url}`;
        try {
            return await this.client.request<T>({
                method,
                url: fullUrl,
                data: body
            });
        } catch (e) {
            throw e;
        }
    }

    public async makeGetRequest<T>(url: string): Promise<AxiosResponse<T>> {
        return this.makeRequest<T>('GET', url);
    }

    public async makePostRequest<T>(url: string, body: any): Promise<AxiosResponse<T>> {
        return this.makeRequest<T>('POST', url, body);
    }

    public async makePatchRequest<T>(url: string, body: any): Promise<AxiosResponse<T>> {
        return this.makeRequest<T>('PATCH', url, body);
    }

    public async makeDeleteRequest<T>(url: string, body: any): Promise<AxiosResponse<T>> {
        return this.makeRequest<T>('DELETE', url, body);
    }

    public async makePutRequest<T>(url: string, body: any): Promise<AxiosResponse<T>> {
        return this.makeRequest<T>('PUT', url, body);
    }

    public async getSummonerName(): Promise<string> {
        try {
            const response = await this.makeGetRequest<SummonerResponse>('/lol-summoner/v1/current-summoner');
            if (response.data.displayName) {
                return response.data.displayName;
            } else if (response.data.gameName) {
                return response.data.gameName;
            }
            throw new LCUError('No summoner name found');
        } catch (e) {
            throw new LCUError(`Error retrieving display name: ${e}`);
        }
    }

    public async getSummonerLevel(): Promise<number> {
        try {
            const response = await this.makeGetRequest<SummonerResponse>('/lol-summoner/v1/current-summoner');
            return response.data.summonerLevel;
        } catch (e) {
            throw new LCUError(`Error retrieving summoner level: ${e}`);
        }
    }

    public async getPatch(): Promise<string> {
        try {
            const response = await this.makeGetRequest<string>('/lol-patch/v1/game-version');
            return response.data.substring(1, 6);
        } catch (e) {
            throw new LCUError(`Error retrieving patch: ${e}`);
        }
    }

    public async getLobbyId(): Promise<number> {
        try {
            const response = await this.makeGetRequest<LobbyResponse>('/lol-lobby/v2/lobby');
            return response.data.gameConfig.queueId;
        } catch (e) {
            throw new LCUError(`Error retrieving lobby ID: ${e}`);
        }
    }

    public async restartUx(): Promise<void> {
        try {
            await this.makePostRequest('/riotclient/kill-and-restart-ux', null);
        } catch (e) {
            throw new LCUError(`Error restarting UX: ${e}`);
        }
    }

    public async accessTokenExists(): Promise<boolean> {
        try {
            await this.makeGetRequest('/rso-auth/v1/authorization');
            return true;
        } catch {
            return false;
        }
    }

    public async getDodgeTimer(): Promise<number> {
        try {
            const response = await this.makeGetRequest<MatchmakingSearch>('/lol-matchmaking/v1/search');
            if (response.data.errors.length > 0) {
                return response.data.errors[0].penaltyTimeRemaining;
            }
            return 0;
        } catch (e) {
            throw new LCUError(`Error getting dodge timer: ${e}`);
        }
    }

    public async getEstimatedQueueTime(): Promise<number> {
        try {
            const response = await this.makeGetRequest<MatchmakingSearch>('/lol-matchmaking/v1/search');
            return response.data.estimatedQueueTime;
        } catch (e) {
            throw new LCUError(`Error retrieving estimated queue time: ${e}`);
        }
    }

    // Continue with other methods following the same pattern...
}