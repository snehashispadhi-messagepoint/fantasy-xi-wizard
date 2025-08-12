import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { 
  XMarkIcon,
  ChartBarIcon,
  ArrowsRightLeftIcon,
  TrophyIcon
} from '@heroicons/react/24/outline';

import Card from '../UI/Card';
import Button from '../UI/Button';
import Badge from '../UI/Badge';
import LoadingSpinner from '../UI/LoadingSpinner';
import RadarChart from '../Charts/RadarChart';
import LineChart from '../Charts/LineChart';

import { useData } from '../../context/DataContext';
import { apiService } from '../../services/apiService';

const PlayerComparison = ({ players, onRemovePlayer, onClose }) => {
  const { formatPrice, getPositionName } = useData();
  const [selectedMetrics, setSelectedMetrics] = useState([
    'total_points',
    'points_per_game', 
    'form',
    'goals_scored',
    'assists',
    'expected_goals',
    'expected_assists',
    'minutes'
  ]);

  // Fetch comparison data
  const {
    data: comparisonData,
    isLoading,
    error
  } = useQuery(
    ['player-comparison', players.map(p => p.id), selectedMetrics],
    async () => {
      const data = await apiService.comparePlayers(players.map(p => p.id), selectedMetrics);
      return data;
    },
    {
      enabled: players.length >= 2,
      staleTime: 5 * 60 * 1000,
    }
  );

  const availableMetrics = [
    { key: 'total_points', label: 'Total Points', category: 'Performance' },
    { key: 'points_per_game', label: 'Points per Game', category: 'Performance' },
    { key: 'form', label: 'Form', category: 'Performance' },
    { key: 'goals_scored', label: 'Goals', category: 'Attacking' },
    { key: 'assists', label: 'Assists', category: 'Attacking' },
    { key: 'expected_goals', label: 'Expected Goals', category: 'Attacking' },
    { key: 'expected_assists', label: 'Expected Assists', category: 'Attacking' },
    { key: 'expected_goal_involvements', label: 'Expected Goal Involvements', category: 'Attacking' },
    { key: 'minutes', label: 'Minutes Played', category: 'General' },
    { key: 'clean_sheets', label: 'Clean Sheets', category: 'Defensive' },
    { key: 'goals_conceded', label: 'Goals Conceded', category: 'Defensive' },
    { key: 'saves', label: 'Saves', category: 'Defensive' },
    { key: 'yellow_cards', label: 'Yellow Cards', category: 'Discipline' },
    { key: 'red_cards', label: 'Red Cards', category: 'Discipline' },
    { key: 'bonus', label: 'Bonus Points', category: 'Performance' },
    { key: 'bps', label: 'Bonus Point System', category: 'Performance' }
  ];

  const metricCategories = [...new Set(availableMetrics.map(m => m.category))];

  const handleMetricToggle = (metricKey) => {
    setSelectedMetrics(prev => 
      prev.includes(metricKey)
        ? prev.filter(m => m !== metricKey)
        : [...prev, metricKey]
    );
  };

  const getPlayerColors = () => {
    const colors = [
      { border: '#3B82F6', background: 'rgba(59, 130, 246, 0.2)' }, // Blue
      { border: '#EF4444', background: 'rgba(239, 68, 68, 0.2)' },  // Red
      { border: '#10B981', background: 'rgba(16, 185, 129, 0.2)' }, // Green
      { border: '#F59E0B', background: 'rgba(245, 158, 11, 0.2)' }, // Yellow
      { border: '#8B5CF6', background: 'rgba(139, 92, 246, 0.2)' }  // Purple
    ];
    return colors;
  };

  const prepareRadarData = () => {
    if (!comparisonData?.radar_chart_data) return null;

    const colors = getPlayerColors();
    
    return {
      labels: comparisonData.radar_chart_data.labels,
      datasets: comparisonData.radar_chart_data.datasets.map((dataset, index) => ({
        ...dataset,
        borderColor: colors[index % colors.length].border,
        backgroundColor: colors[index % colors.length].background
      }))
    };
  };

  const prepareLineData = () => {
    if (!comparisonData?.line_chart_data) return null;

    const colors = getPlayerColors();
    
    return {
      labels: comparisonData.line_chart_data.labels,
      datasets: comparisonData.line_chart_data.datasets.map((dataset, index) => ({
        ...dataset,
        borderColor: colors[index % colors.length].border,
        backgroundColor: colors[index % colors.length].background,
        fill: false
      }))
    };
  };

  if (players.length < 2) {
    return (
      <Card title="Player Comparison" className="text-center">
        <div className="py-8">
          <ArrowsRightLeftIcon className="h-16 w-16 text-dark-500 mx-auto mb-4" />
          <p className="text-dark-400 mb-2">Select at least 2 players to compare</p>
          <p className="text-sm text-dark-500">
            Use the player selection from the Players page to add players for comparison
          </p>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <ArrowsRightLeftIcon className="h-6 w-6 text-primary-500" />
            <div>
              <h2 className="text-xl font-bold text-white">Player Comparison</h2>
              <p className="text-sm text-dark-400">
                Comparing {players.length} players across {selectedMetrics.length} metrics
              </p>
            </div>
          </div>
          {onClose && (
            <Button variant="ghost" size="sm" onClick={onClose}>
              <XMarkIcon className="h-5 w-5" />
            </Button>
          )}
        </div>
      </Card>

      {/* Selected Players */}
      <Card title="Selected Players">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {players.map((player, index) => {
            const colors = getPlayerColors();
            const playerColor = colors[index % colors.length];
            
            return (
              <div 
                key={player.id}
                className="bg-dark-800 rounded-lg p-4 border-l-4"
                style={{ borderLeftColor: playerColor.border }}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-semibold text-white">{player.web_name}</h3>
                    <p className="text-sm text-dark-400">{player.team?.name}</p>
                    <div className="flex items-center space-x-2 mt-2">
                      <Badge variant="outline" size="sm">
                        {getPositionName(player.element_type)}
                      </Badge>
                      <Badge variant="outline" size="sm">
                        £{formatPrice(player.now_cost)}
                      </Badge>
                    </div>
                  </div>
                  {onRemovePlayer && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onRemovePlayer(player.id)}
                    >
                      <XMarkIcon className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      {/* Metric Selection */}
      <Card title="Select Metrics" subtitle="Choose which statistics to compare">
        <div className="space-y-4">
          {metricCategories.map(category => (
            <div key={category}>
              <h4 className="text-sm font-medium text-white mb-2">{category}</h4>
              <div className="flex flex-wrap gap-2">
                {availableMetrics
                  .filter(metric => metric.category === category)
                  .map(metric => (
                    <button
                      key={metric.key}
                      onClick={() => handleMetricToggle(metric.key)}
                      className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                        selectedMetrics.includes(metric.key)
                          ? 'bg-primary-600 text-white'
                          : 'bg-dark-700 text-dark-300 hover:bg-dark-600'
                      }`}
                    >
                      {metric.label}
                    </button>
                  ))}
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Comparison Results */}
      {isLoading ? (
        <Card>
          <LoadingSpinner size="lg" text="Analyzing player data..." />
        </Card>
      ) : error ? (
        <Card title="Error" className="border-danger-700">
          <div className="text-center py-8">
            <p className="text-danger-400 mb-4">
              Failed to load comparison data: {error.message}
            </p>
            <Button variant="primary" onClick={() => window.location.reload()}>
              Try Again
            </Button>
          </div>
        </Card>
      ) : comparisonData ? (
        <>
          {/* Radar Chart */}
          <Card title="Performance Radar" subtitle="Overall comparison across all metrics">
            <div className="flex justify-center">
              <RadarChart 
                data={prepareRadarData()} 
                width={500} 
                height={500}
                className="bg-dark-800 rounded-lg p-4"
              />
            </div>
          </Card>

          {/* Line Chart */}
          {comparisonData.line_chart_data && (
            <Card title="Form Trend" subtitle="Recent performance over time">
              <LineChart 
                data={prepareLineData()} 
                width={700} 
                height={350}
                className="bg-dark-800 rounded-lg p-4"
              />
            </Card>
          )}

          {/* Detailed Comparison Table */}
          <Card title="Detailed Comparison" subtitle="Side-by-side statistics">
            <div className="overflow-x-auto">
              <table className="table">
                <thead>
                  <tr>
                    <th className="px-6 py-3">Metric</th>
                    {players.map((player, index) => {
                      const colors = getPlayerColors();
                      const playerColor = colors[index % colors.length];
                      return (
                        <th 
                          key={player.id} 
                          className="px-6 py-3"
                          style={{ color: playerColor.border }}
                        >
                          {player.web_name}
                        </th>
                      );
                    })}
                    <th className="px-6 py-3">Winner</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedMetrics.map(metric => {
                    const metricData = comparisonData.comparison_data[metric];
                    if (!metricData) return null;

                    const winner = metricData.reduce((max, current) => 
                      current.value > max.value ? current : max
                    );

                    return (
                      <tr key={metric}>
                        <td className="px-6 py-4 font-medium text-white">
                          {availableMetrics.find(m => m.key === metric)?.label || metric}
                        </td>
                        {metricData.map((playerData, index) => {
                          const colors = getPlayerColors();
                          const playerColor = colors[index % colors.length];
                          const isWinner = playerData.player_id === winner.player_id;
                          
                          return (
                            <td 
                              key={playerData.player_id} 
                              className={`px-6 py-4 ${isWinner ? 'font-bold' : ''}`}
                              style={{ color: isWinner ? playerColor.border : '#F3F4F6' }}
                            >
                              {typeof playerData.value === 'number' 
                                ? playerData.value.toFixed(1) 
                                : playerData.value}
                            </td>
                          );
                        })}
                        <td className="px-6 py-4">
                          <div className="flex items-center space-x-1">
                            <TrophyIcon className="h-4 w-4 text-yellow-500" />
                            <span className="text-white text-sm">
                              {winner.player_name}
                            </span>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Summary */}
          {comparisonData.summary && (
            <Card title="Analysis Summary">
              <div className="bg-dark-800 rounded-lg p-4">
                <p className="text-dark-300">{comparisonData.summary}</p>
                {comparisonData.winner && (
                  <div className="mt-3 flex items-center space-x-2">
                    <TrophyIcon className="h-5 w-5 text-yellow-500" />
                    <span className="text-white font-medium">
                      Overall Winner: {comparisonData.winner}
                    </span>
                  </div>
                )}
              </div>
            </Card>
          )}
        </>
      ) : null}
    </div>
  );
};

export default PlayerComparison;
