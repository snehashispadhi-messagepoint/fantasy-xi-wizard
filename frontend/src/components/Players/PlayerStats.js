import React from 'react';
import { 
  TrophyIcon, 
  FireIcon, 
  CurrencyPoundIcon,
  UsersIcon 
} from '@heroicons/react/24/outline';
import Card from '../UI/Card';

const PlayerStats = ({ players, isLoading = false }) => {
  if (isLoading || !players || players.length === 0) {
    return null;
  }

  // Calculate statistics
  const stats = {
    topScorer: players.reduce((max, player) => 
      player.total_points > (max?.total_points || 0) ? player : max, null),
    
    bestForm: players.reduce((max, player) => 
      player.form > (max?.form || 0) ? player : max, null),
    
    mostExpensive: players.reduce((max, player) => 
      player.now_cost > (max?.now_cost || 0) ? player : max, null),
    
    mostOwned: players.reduce((max, player) => 
      player.selected_by_percent > (max?.selected_by_percent || 0) ? player : max, null),
    
    averagePrice: players.reduce((sum, player) => sum + player.now_cost, 0) / players.length / 10,
    averagePoints: players.reduce((sum, player) => sum + player.total_points, 0) / players.length,
    totalPlayers: players.length
  };

  const StatCard = ({ icon: Icon, title, player, value, subtitle, color = 'primary' }) => (
    <div className="bg-dark-800 rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <Icon className={`h-6 w-6 text-${color}-500`} />
        <span className="text-xs text-dark-400">{title}</span>
      </div>
      
      {player ? (
        <div>
          <p className="text-lg font-bold text-white">{player.web_name}</p>
          <p className="text-sm text-dark-400">{player.team?.short_name}</p>
          <p className="text-xs text-dark-500 mt-1">{subtitle}</p>
        </div>
      ) : (
        <div>
          <p className="text-lg font-bold text-white">{value}</p>
          <p className="text-sm text-dark-400">{subtitle}</p>
        </div>
      )}
    </div>
  );

  return (
    <Card title="Quick Stats" subtitle={`Based on ${stats.totalPlayers} players`}>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={TrophyIcon}
          title="Top Scorer"
          player={stats.topScorer}
          subtitle={`${stats.topScorer?.total_points} points`}
          color="success"
        />
        
        <StatCard
          icon={FireIcon}
          title="Best Form"
          player={stats.bestForm}
          subtitle={`${stats.bestForm?.form} form`}
          color="danger"
        />
        
        <StatCard
          icon={CurrencyPoundIcon}
          title="Most Expensive"
          player={stats.mostExpensive}
          subtitle={`£${(stats.mostExpensive?.now_cost / 10).toFixed(1)}m`}
          color="warning"
        />
        
        <StatCard
          icon={UsersIcon}
          title="Most Owned"
          player={stats.mostOwned}
          subtitle={`${stats.mostOwned?.selected_by_percent}% owned`}
          color="primary"
        />
      </div>
      
      {/* Summary Stats */}
      <div className="mt-4 pt-4 border-t border-dark-700">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-sm text-dark-400">Average Price</p>
            <p className="text-lg font-semibold text-white">£{stats.averagePrice.toFixed(1)}m</p>
          </div>
          <div>
            <p className="text-sm text-dark-400">Average Points</p>
            <p className="text-lg font-semibold text-white">{stats.averagePoints.toFixed(1)}</p>
          </div>
          <div>
            <p className="text-sm text-dark-400">Total Players</p>
            <p className="text-lg font-semibold text-white">{stats.totalPlayers}</p>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default PlayerStats;
