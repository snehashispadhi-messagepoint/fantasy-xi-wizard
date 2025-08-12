import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth headers here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API Error:', error);
    
    if (error.response) {
      // Server responded with error status
      throw new Error(error.response.data?.message || 'Server error occurred');
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Network error - please check your connection');
    } else {
      // Something else happened
      throw new Error('An unexpected error occurred');
    }
  }
);

export const apiService = {
  // Players
  getPlayers: (params = {}) => {
    return api.get('/players/', { params });
  },
  
  getPlayer: (playerId) => {
    return api.get(`/players/${playerId}/`);
  },

  getPlayerStats: (playerId, params = {}) => {
    return api.get(`/players/${playerId}/stats/`, { params });
  },

  searchPlayers: (query, limit = 10) => {
    return api.get(`/players/search/${encodeURIComponent(query)}/`, {
      params: { limit }
    });
  },

  comparePlayers: (playerIds, metrics = null) => {
    return api.post('/players/compare/', {
      player_ids: playerIds,
      metrics
    });
  },

  // Teams
  getTeams: () => {
    return api.get('/teams/');
  },
  
  getTeam: (teamId) => {
    return api.get(`/teams/${teamId}/`);
  },

  getTeamStats: (teamId, season = null) => {
    return api.get(`/teams/${teamId}/stats/`, {
      params: season ? { season } : {}
    });
  },
  
  getTeamFixtures: (teamId, nextGameweeks = 3) => {
    return api.get(`/teams/${teamId}/fixtures`, {
      params: { next_gameweeks: nextGameweeks }
    });
  },
  
  getTeamDifficulty: (teamId, nextGameweeks = 3) => {
    return api.get(`/teams/${teamId}/difficulty`, {
      params: { next_gameweeks: nextGameweeks }
    });
  },

  // Fixtures
  getFixtures: (params = {}) => {
    return api.get('/fixtures', { params });
  },
  
  getGameweekFixtures: (gameweek) => {
    return api.get(`/fixtures/gameweek/${gameweek}`);
  },
  
  getFixtureDifficulty: (nextGameweeks = 3) => {
    return api.get('/fixtures/difficulty', {
      params: { next_gameweeks: nextGameweeks }
    });
  },
  
  getCurrentGameweek: () => {
    return api.get('/fixtures/current-gameweek');
  },
  
  getNextDeadline: () => {
    return api.get('/fixtures/next-deadline');
  },

  // Statistics
  getPlayerComparison: (playerIds, metrics = null, season = null) => {
    const params = new URLSearchParams();
    playerIds.forEach(id => params.append('player_ids', id));
    if (metrics) metrics.forEach(metric => params.append('metrics', metric));
    if (season) params.append('season', season);
    
    return api.get(`/stats/player-comparison?${params.toString()}`);
  },
  
  getTeamPerformance: (season = null, metric = 'points') => {
    return api.get('/stats/team-performance', {
      params: { season, metric }
    });
  },
  
  getSeasonSummary: (season = '2025-26') => {
    return api.get('/stats/season-summary', {
      params: { season }
    });
  },
  
  getTrendAnalysis: (params = {}) => {
    return api.get('/stats/trends', { params });
  },
  
  getTopPerformers: (position = null, metric = 'total_points', limit = 10, gameweeks = null) => {
    const params = { metric, limit };
    if (position) params.position = position;
    if (gameweeks) params.gameweeks = gameweeks;
    return api.get('/stats/top-performers', { params });
  },

  getFormTable: (gameweeks = 5) => {
    return api.get('/stats/form-table', {
      params: { gameweeks }
    });
  },
  
  getFormTable: (gameweeks = 5, position = null) => {
    return api.get('/stats/form-table', {
      params: { gameweeks, position }
    });
  },

  // AI-Powered Recommendations
  getSquadRecommendation: (budget = 100.0, formation = '3-5-2', gameweeks = 3, userPreferences = null) => {
    const params = new URLSearchParams({
      budget: budget.toString(),
      formation,
      gameweeks: gameweeks.toString()
    });
    return api.post(`/recommendations/squad?${params}`, userPreferences || {});
  },

  getTransferRecommendation: (currentSquad = [], budget = 0.0, freeTransfers = 1, gameweeks = 3) => {
    return api.post('/recommendations/ai-transfers', {
      current_squad: currentSquad,
      budget,
      free_transfers: freeTransfers,
      gameweeks
    });
  },

  getCaptainRecommendation: (squad = null, gameweek = null) => {
    const params = new URLSearchParams();
    if (gameweek) params.append('gameweek', gameweek.toString());
    return api.post(`/recommendations/ai-captain?${params}`, squad ? { squad } : {});
  },

  getChipRecommendation: (remainingChips = ['triple_captain', 'bench_boost', 'free_hit'], currentGameweek = 1) => {
    return api.post('/recommendations/ai-chips', {
      remaining_chips: remainingChips,
      current_gameweek: currentGameweek
    });
  },

  queryAI: (query, context = null) => {
    return api.post('/recommendations/query', {
      query,
      context
    });
  },

  // Admin
  getDatabaseStats: () => {
    return api.get('/admin/database-stats');
  },
  
  getApiHealth: () => {
    return api.get('/admin/api-health');
  },
  
  getSystemInfo: () => {
    return api.get('/admin/system-info');
  },
  
  syncData: (force = false) => {
    return api.post('/admin/sync-data', null, {
      params: { force }
    });
  },
};

export default apiService;
