import React, { useState } from 'react';
import { 
  XMarkIcon,
  ChartBarIcon,
  TrophyIcon,
  UserGroupIcon,
  CalendarDaysIcon
} from '@heroicons/react/24/outline';

import Button from '../UI/Button';
import Card from '../UI/Card';
import Badge from '../UI/Badge';
import TeamBadge from '../UI/TeamBadge';

const TeamComparison = ({ 
  teams = [], 
  allTeams = [],
  onClose,
  isOpen 
}) => {
  const [selectedTeams, setSelectedTeams] = useState(teams.slice(0, 2));

  if (!isOpen) return null;

  const addTeam = (team) => {
    if (selectedTeams.length < 4 && !selectedTeams.find(t => t.id === team.id)) {
      setSelectedTeams([...selectedTeams, team]);
    }
  };

  const removeTeam = (teamId) => {
    setSelectedTeams(selectedTeams.filter(t => t.id !== teamId));
  };

  const getComparisonValue = (team, metric) => {
    switch (metric) {
      case 'points': return team.stats?.points || 0;
      case 'players': return team.players?.length || 0;
      case 'form': return parseFloat(team.stats?.form) || 0;
      case 'home_strength': return team.stats?.strength_overall_home || 0;
      case 'away_strength': return team.stats?.strength_overall_away || 0;
      case 'attack_home': return team.stats?.strength_attack_home || 0;
      case 'attack_away': return team.stats?.strength_attack_away || 0;
      case 'defence_home': return team.stats?.strength_defence_home || 0;
      case 'defence_away': return team.stats?.strength_defence_away || 0;
      case 'avg_price': 
        const totalCost = team.players?.reduce((sum, p) => sum + (p.now_cost || 0), 0) || 0;
        return team.players?.length ? (totalCost / 10 / team.players.length) : 0;
      default: return 0;
    }
  };

  const getBestTeam = (metric) => {
    if (selectedTeams.length === 0) return null;
    return selectedTeams.reduce((best, team) => 
      getComparisonValue(team, metric) > getComparisonValue(best, metric) ? team : best
    );
  };

  const getBarWidth = (team, metric) => {
    const values = selectedTeams.map(t => getComparisonValue(t, metric));
    const maxValue = Math.max(...values);
    const minValue = Math.min(...values);
    const range = maxValue - minValue;
    
    if (range === 0) return 100;
    
    const value = getComparisonValue(team, metric);
    return ((value - minValue) / range) * 100;
  };

  const comparisonMetrics = [
    { key: 'points', label: 'Total Points', format: (v) => v.toFixed(0) },
    { key: 'players', label: 'Squad Size', format: (v) => v.toFixed(0) },
    { key: 'form', label: 'Form', format: (v) => v.toFixed(1) },
    { key: 'home_strength', label: 'Home Strength', format: (v) => v.toFixed(0) },
    { key: 'away_strength', label: 'Away Strength', format: (v) => v.toFixed(0) },
    { key: 'attack_home', label: 'Home Attack', format: (v) => v.toFixed(0) },
    { key: 'attack_away', label: 'Away Attack', format: (v) => v.toFixed(0) },
    { key: 'defence_home', label: 'Home Defence', format: (v) => v.toFixed(0) },
    { key: 'defence_away', label: 'Away Defence', format: (v) => v.toFixed(0) },
    { key: 'avg_price', label: 'Avg Player Price', format: (v) => `£${v.toFixed(1)}m` }
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-dark-900 rounded-xl border border-dark-700 w-full max-w-6xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-dark-700">
          <div className="flex items-center space-x-3">
            <ChartBarIcon className="h-6 w-6 text-primary-500" />
            <h2 className="text-xl font-bold text-white">Team Comparison</h2>
          </div>
          <Button
            variant="secondary"
            size="sm"
            onClick={onClose}
            icon={<XMarkIcon className="h-4 w-4" />}
          >
            Close
          </Button>
        </div>

        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {/* Team Selection */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-white mb-4">
              Selected Teams ({selectedTeams.length}/4)
            </h3>
            
            {/* Selected Teams */}
            <div className="flex flex-wrap gap-3 mb-4">
              {selectedTeams.map(team => (
                <div key={team.id} className="flex items-center space-x-2 bg-dark-800 rounded-lg p-3">
                  <TeamBadge team={team} size="sm" />
                  <span className="text-white font-medium">{team.short_name}</span>
                  <button
                    onClick={() => removeTeam(team.id)}
                    className="text-danger-400 hover:text-danger-300"
                  >
                    <XMarkIcon className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>

            {/* Add Teams */}
            {selectedTeams.length < 4 && (
              <div>
                <h4 className="text-md font-medium text-white mb-2">Add Teams:</h4>
                <div className="flex flex-wrap gap-2">
                  {allTeams
                    .filter(team => !selectedTeams.find(t => t.id === team.id))
                    .slice(0, 10)
                    .map(team => (
                      <button
                        key={team.id}
                        onClick={() => addTeam(team)}
                        className="flex items-center space-x-2 bg-dark-700 hover:bg-dark-600 rounded-lg p-2 transition-colors"
                      >
                        <TeamBadge team={team} size="xs" />
                        <span className="text-white text-sm">{team.short_name}</span>
                      </button>
                    ))}
                </div>
              </div>
            )}
          </div>

          {/* Comparison Table */}
          {selectedTeams.length >= 2 && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-white">Comparison Metrics</h3>
              
              <div className="space-y-4">
                {comparisonMetrics.map(metric => {
                  const bestTeam = getBestTeam(metric.key);
                  
                  return (
                    <div key={metric.key} className="bg-dark-800 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="text-white font-medium">{metric.label}</h4>
                        {bestTeam && (
                          <div className="flex items-center space-x-2">
                            <span className="text-xs text-dark-400">Best:</span>
                            <TeamBadge team={bestTeam} size="xs" />
                            <span className="text-success-400 text-sm font-medium">
                              {metric.format(getComparisonValue(bestTeam, metric.key))}
                            </span>
                          </div>
                        )}
                      </div>
                      
                      <div className="space-y-2">
                        {selectedTeams.map(team => {
                          const value = getComparisonValue(team, metric.key);
                          const barWidth = getBarWidth(team, metric.key);
                          const isBest = bestTeam && team.id === bestTeam.id;
                          
                          return (
                            <div key={team.id} className="flex items-center space-x-3">
                              <div className="flex items-center space-x-2 w-24">
                                <TeamBadge team={team} size="xs" />
                                <span className="text-white text-sm">{team.short_name}</span>
                              </div>
                              
                              <div className="flex-1 relative">
                                <div className="w-full bg-dark-700 rounded-full h-2">
                                  <div 
                                    className={`h-2 rounded-full transition-all duration-300 ${
                                      isBest ? 'bg-success-500' : 'bg-primary-500'
                                    }`}
                                    style={{ width: `${Math.max(barWidth, 5)}%` }}
                                  />
                                </div>
                              </div>
                              
                              <div className="w-20 text-right">
                                <span className={`text-sm font-medium ${
                                  isBest ? 'text-success-400' : 'text-white'
                                }`}>
                                  {metric.format(value)}
                                </span>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Summary */}
              <div className="bg-dark-800 rounded-lg p-4">
                <h4 className="text-white font-medium mb-3">Summary</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {selectedTeams.map(team => {
                    const wins = comparisonMetrics.filter(metric => {
                      const bestTeam = getBestTeam(metric.key);
                      return bestTeam && bestTeam.id === team.id;
                    }).length;
                    
                    return (
                      <div key={team.id} className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <TeamBadge team={team} size="sm" />
                          <span className="text-white font-medium">{team.name}</span>
                        </div>
                        <Badge variant={wins >= 5 ? 'success' : wins >= 3 ? 'primary' : 'outline'}>
                          {wins} wins
                        </Badge>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {selectedTeams.length < 2 && (
            <div className="text-center py-12">
              <ChartBarIcon className="h-12 w-12 text-dark-500 mx-auto mb-4" />
              <p className="text-dark-400">
                Select at least 2 teams to start comparing
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TeamComparison;
