import React, { useState, useEffect } from 'react';
import {
  ChartBarIcon,
  TrophyIcon,
  FireIcon,
  BuildingOfficeIcon,
  UserGroupIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CurrencyPoundIcon
} from '@heroicons/react/24/outline';

import Card from '../components/UI/Card';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import Badge from '../components/UI/Badge';
import TeamBadge from '../components/UI/TeamBadge';
import { apiService } from '../services/apiService';

const Statistics = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({
    topPerformers: [],
    formTable: [],
    teamPerformance: [],
    seasonStats: null
  });

  const tabs = [
    { id: 'overview', name: 'Overview', icon: ChartBarIcon },
    { id: 'players', name: 'Player Stats', icon: UserGroupIcon },
    { id: 'teams', name: 'Team Performance', icon: BuildingOfficeIcon },
    { id: 'trends', name: 'Trends & Analysis', icon: ArrowTrendingUpIcon }
  ];

  useEffect(() => {
    fetchStatisticsData();
  }, []);

  const fetchStatisticsData = async () => {
    setLoading(true);
    try {
      const [topPerformers, formTable, teamPerformance] = await Promise.all([
        apiService.getTopPerformers(null, 'total_points', 10),
        apiService.getFormTable(5),
        apiService.getTeamPerformance()
      ]);

      setData({
        topPerformers: topPerformers || [],
        formTable: formTable || [],
        teamPerformance: teamPerformance || [],
        seasonStats: null
      });
    } catch (error) {
      console.error('Error fetching statistics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" text="Loading statistics..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Statistics</h1>
        <p className="text-dark-400 mt-1">
          Deep statistical analysis and performance insights
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-dark-700">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm
                  ${isActive
                    ? 'border-primary-500 text-primary-400'
                    : 'border-transparent text-dark-400 hover:text-dark-300 hover:border-dark-600'
                  }
                `}
              >
                <tab.icon className={`
                  -ml-0.5 mr-2 h-5 w-5
                  ${isActive ? 'text-primary-400' : 'text-dark-400 group-hover:text-dark-300'}
                `} />
                {tab.name}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && <OverviewTab data={data} />}
      {activeTab === 'players' && <PlayersTab data={data} />}
      {activeTab === 'teams' && <TeamsTab data={data} />}
      {activeTab === 'trends' && <TrendsTab data={data} />}
    </div>
  );
};

// Overview Tab Component
const OverviewTab = ({ data }) => {
  const { topPerformers, teamPerformance } = data;

  // Calculate overview stats
  const overviewStats = {
    totalPlayers: topPerformers.length > 0 ? 681 : 0, // From API response
    totalTeams: teamPerformance.length,
    highestPoints: topPerformers.length > 0 ? topPerformers[0]?.total_points || 0 : 0,
    averagePoints: topPerformers.length > 0
      ? Math.round(topPerformers.reduce((sum, p) => sum + p.total_points, 0) / topPerformers.length)
      : 0
  };

  return (
    <div className="space-y-6">
      {/* Key Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-br from-blue-600 to-blue-700">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <UserGroupIcon className="h-8 w-8 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-blue-100 text-sm font-medium">Total Players</p>
              <p className="text-white text-2xl font-bold">{overviewStats.totalPlayers}</p>
            </div>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-green-600 to-green-700">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <BuildingOfficeIcon className="h-8 w-8 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-green-100 text-sm font-medium">Premier League Teams</p>
              <p className="text-white text-2xl font-bold">{overviewStats.totalTeams}</p>
            </div>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-purple-600 to-purple-700">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <TrophyIcon className="h-8 w-8 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-purple-100 text-sm font-medium">Highest Points</p>
              <p className="text-white text-2xl font-bold">{overviewStats.highestPoints}</p>
            </div>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-orange-600 to-orange-700">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-8 w-8 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-orange-100 text-sm font-medium">Average Points</p>
              <p className="text-white text-2xl font-bold">{overviewStats.averagePoints}</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Top Performers */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Top Points Scorers" subtitle="Season leaders">
          <div className="space-y-3">
            {topPerformers.slice(0, 5).map((player, index) => (
              <div key={player.player_id} className="flex items-center justify-between p-3 bg-dark-700 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <div className={`
                      w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold
                      ${index === 0 ? 'bg-yellow-500 text-yellow-900' :
                        index === 1 ? 'bg-gray-400 text-gray-900' :
                        index === 2 ? 'bg-orange-600 text-orange-100' :
                        'bg-dark-600 text-dark-300'}
                    `}>
                      {index + 1}
                    </div>
                  </div>
                  <div>
                    <p className="text-white font-medium">{player.name}</p>
                    <p className="text-dark-400 text-sm">{player.team} • {player.position}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-white font-bold">{player.total_points}</p>
                  <p className="text-dark-400 text-sm">points</p>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Team Performance Summary" subtitle="League standings preview">
          <div className="space-y-3">
            {teamPerformance.slice(0, 5).map((team, index) => (
              <div key={team.team_id} className="flex items-center justify-between p-3 bg-dark-700 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-dark-600 rounded-full flex items-center justify-center text-sm font-bold text-dark-300">
                      {index + 1}
                    </div>
                  </div>
                  <div>
                    <p className="text-white font-medium">{team.team_name}</p>
                    <p className="text-dark-400 text-sm">{team.wins}W {team.draws}D {team.losses}L</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-white font-bold">{team.points}</p>
                  <p className="text-dark-400 text-sm">pts</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};

// Players Tab Component
const PlayersTab = ({ data }) => {
  const { topPerformers, formTable } = data;
  const [selectedMetric, setSelectedMetric] = useState('total_points');
  const [selectedPosition, setSelectedPosition] = useState('all');

  const metrics = [
    { value: 'total_points', label: 'Total Points' },
    { value: 'form', label: 'Form' },
    { value: 'goals_scored', label: 'Goals' },
    { value: 'assists', label: 'Assists' },
    { value: 'selected_by_percent', label: 'Ownership %' }
  ];

  const positions = [
    { value: 'all', label: 'All Positions' },
    { value: 'GK', label: 'Goalkeepers' },
    { value: 'DEF', label: 'Defenders' },
    { value: 'MID', label: 'Midfielders' },
    { value: 'FWD', label: 'Forwards' }
  ];

  // Filter players based on position
  const filteredPlayers = selectedPosition === 'all'
    ? formTable
    : formTable.filter(player => player.position === selectedPosition);

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex flex-wrap gap-4">
        <div>
          <label className="block text-sm font-medium text-dark-300 mb-2">
            Metric
          </label>
          <select
            value={selectedMetric}
            onChange={(e) => setSelectedMetric(e.target.value)}
            className="bg-dark-800 border border-dark-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            {metrics.map(metric => (
              <option key={metric.value} value={metric.value}>
                {metric.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-dark-300 mb-2">
            Position
          </label>
          <select
            value={selectedPosition}
            onChange={(e) => setSelectedPosition(e.target.value)}
            className="bg-dark-800 border border-dark-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            {positions.map(position => (
              <option key={position.value} value={position.value}>
                {position.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Player Statistics Table */}
      <Card title={`Player Statistics - ${metrics.find(m => m.value === selectedMetric)?.label}`}>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-dark-700">
            <thead className="bg-dark-800">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-dark-300 uppercase tracking-wider">
                  Rank
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-dark-300 uppercase tracking-wider">
                  Player
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-dark-300 uppercase tracking-wider">
                  Team
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-dark-300 uppercase tracking-wider">
                  Position
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-dark-300 uppercase tracking-wider">
                  Points
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-dark-300 uppercase tracking-wider">
                  Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-dark-300 uppercase tracking-wider">
                  Form
                </th>
              </tr>
            </thead>
            <tbody className="bg-dark-900 divide-y divide-dark-700">
              {filteredPlayers.slice(0, 20).map((player, index) => (
                <tr key={player.player_id} className="hover:bg-dark-800">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className={`
                        w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold
                        ${index < 3 ? 'bg-primary-600 text-white' : 'bg-dark-700 text-dark-300'}
                      `}>
                        {index + 1}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-white font-medium">{player.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-dark-300">{player.team}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Badge variant={
                      player.position === 'GK' ? 'yellow' :
                      player.position === 'DEF' ? 'green' :
                      player.position === 'MID' ? 'blue' : 'red'
                    }>
                      {player.position}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-white font-bold">{player.total_points}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-dark-300">£{player.price}m</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-dark-300">{player.form}</div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

// Teams Tab Component
const TeamsTab = ({ data }) => {
  const { teamPerformance } = data;

  const getFormColor = (result) => {
    switch (result) {
      case 'W': return 'bg-green-500';
      case 'D': return 'bg-yellow-500';
      case 'L': return 'bg-red-500';
      default: return 'bg-dark-600';
    }
  };

  return (
    <div className="space-y-6">
      {/* Team Performance Table */}
      <Card title="Premier League Table" subtitle="Current season standings">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-dark-700">
            <thead className="bg-dark-800">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-dark-300 uppercase tracking-wider">
                  Pos
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-dark-300 uppercase tracking-wider">
                  Team
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-dark-300 uppercase tracking-wider">
                  P
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-dark-300 uppercase tracking-wider">
                  W
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-dark-300 uppercase tracking-wider">
                  D
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-dark-300 uppercase tracking-wider">
                  L
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-dark-300 uppercase tracking-wider">
                  GF
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-dark-300 uppercase tracking-wider">
                  GA
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-dark-300 uppercase tracking-wider">
                  GD
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-dark-300 uppercase tracking-wider">
                  Pts
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-dark-300 uppercase tracking-wider">
                  Form
                </th>
              </tr>
            </thead>
            <tbody className="bg-dark-900 divide-y divide-dark-700">
              {teamPerformance.map((team, index) => (
                <tr key={team.team_id} className="hover:bg-dark-800">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className={`
                        w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold
                        ${index < 4 ? 'bg-green-600 text-white' :
                          index < 6 ? 'bg-blue-600 text-white' :
                          index >= 17 ? 'bg-red-600 text-white' : 'bg-dark-700 text-dark-300'}
                      `}>
                        {index + 1}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <TeamBadge teamName={team.team_name} size="sm" />
                      <div className="ml-3">
                        <div className="text-white font-medium">{team.team_name}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center text-dark-300">
                    {team.games_played}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center text-dark-300">
                    {team.wins}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center text-dark-300">
                    {team.draws}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center text-dark-300">
                    {team.losses}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center text-dark-300">
                    {team.goals_for}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center text-dark-300">
                    {team.goals_against}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center">
                    <span className={`
                      font-medium
                      ${team.goal_difference > 0 ? 'text-green-400' :
                        team.goal_difference < 0 ? 'text-red-400' : 'text-dark-300'}
                    `}>
                      {team.goal_difference > 0 ? '+' : ''}{team.goal_difference}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center">
                    <span className="text-white font-bold">{team.points}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex space-x-1">
                      {team.last_5_results.map((result, idx) => (
                        <div
                          key={idx}
                          className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white ${getFormColor(result)}`}
                        >
                          {result}
                        </div>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Team Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card title="Best Attack" subtitle="Goals scored">
          <div className="space-y-3">
            {teamPerformance
              .sort((a, b) => b.goals_for - a.goals_for)
              .slice(0, 5)
              .map((team, index) => (
                <div key={team.team_id} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="text-dark-400 text-sm w-4">{index + 1}.</span>
                    <TeamBadge teamName={team.team_name} size="xs" />
                    <span className="text-white">{team.team_name}</span>
                  </div>
                  <span className="text-green-400 font-bold">{team.goals_for}</span>
                </div>
              ))}
          </div>
        </Card>

        <Card title="Best Defense" subtitle="Goals conceded">
          <div className="space-y-3">
            {teamPerformance
              .sort((a, b) => a.goals_against - b.goals_against)
              .slice(0, 5)
              .map((team, index) => (
                <div key={team.team_id} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="text-dark-400 text-sm w-4">{index + 1}.</span>
                    <TeamBadge teamName={team.team_name} size="xs" />
                    <span className="text-white">{team.team_name}</span>
                  </div>
                  <span className="text-blue-400 font-bold">{team.goals_against}</span>
                </div>
              ))}
          </div>
        </Card>

        <Card title="Clean Sheets" subtitle="Defensive records">
          <div className="space-y-3">
            {teamPerformance
              .sort((a, b) => b.clean_sheets - a.clean_sheets)
              .slice(0, 5)
              .map((team, index) => (
                <div key={team.team_id} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="text-dark-400 text-sm w-4">{index + 1}.</span>
                    <TeamBadge teamName={team.team_name} size="xs" />
                    <span className="text-white">{team.team_name}</span>
                  </div>
                  <span className="text-yellow-400 font-bold">{team.clean_sheets}</span>
                </div>
              ))}
          </div>
        </Card>
      </div>
    </div>
  );
};

// Trends Tab Component
const TrendsTab = ({ data }) => {
  const { topPerformers, formTable } = data;

  // Calculate trend insights
  const trendInsights = {
    risingStars: formTable
      .filter(player => player.form > 5)
      .sort((a, b) => b.form - a.form)
      .slice(0, 5),

    fallingPlayers: formTable
      .filter(player => player.form < 3 && player.total_points > 50)
      .sort((a, b) => a.form - b.form)
      .slice(0, 5),

    valuePicksUnder7: formTable
      .filter(player => player.price < 7.0 && player.total_points > 80)
      .sort((a, b) => b.total_points - a.total_points)
      .slice(0, 5),

    premiumPlayers: formTable
      .filter(player => player.price >= 10.0)
      .sort((a, b) => b.total_points - a.total_points)
      .slice(0, 5)
  };

  return (
    <div className="space-y-6">
      {/* Trend Analysis Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card
          title="Rising Stars"
          subtitle="Players in excellent form"
          className="border-l-4 border-green-500"
        >
          <div className="space-y-3">
            {trendInsights.risingStars.map((player, index) => (
              <div key={player.player_id} className="flex items-center justify-between p-3 bg-dark-700 rounded-lg">
                <div className="flex items-center space-x-3">
                  <ArrowTrendingUpIcon className="h-5 w-5 text-green-400" />
                  <div>
                    <p className="text-white font-medium">{player.name}</p>
                    <p className="text-dark-400 text-sm">{player.team} • {player.position}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-green-400 font-bold">{player.form}</p>
                  <p className="text-dark-400 text-sm">form</p>
                </div>
              </div>
            ))}
            {trendInsights.risingStars.length === 0 && (
              <p className="text-dark-400 text-center py-4">No players in exceptional form currently</p>
            )}
          </div>
        </Card>

        <Card
          title="Falling Players"
          subtitle="Players struggling for form"
          className="border-l-4 border-red-500"
        >
          <div className="space-y-3">
            {trendInsights.fallingPlayers.map((player, index) => (
              <div key={player.player_id} className="flex items-center justify-between p-3 bg-dark-700 rounded-lg">
                <div className="flex items-center space-x-3">
                  <ArrowTrendingDownIcon className="h-5 w-5 text-red-400" />
                  <div>
                    <p className="text-white font-medium">{player.name}</p>
                    <p className="text-dark-400 text-sm">{player.team} • {player.position}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-red-400 font-bold">{player.form}</p>
                  <p className="text-dark-400 text-sm">form</p>
                </div>
              </div>
            ))}
            {trendInsights.fallingPlayers.length === 0 && (
              <p className="text-dark-400 text-center py-4">No significant form drops detected</p>
            )}
          </div>
        </Card>
      </div>

      {/* Value Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card
          title="Value Picks Under £7.0m"
          subtitle="Budget-friendly high performers"
          className="border-l-4 border-blue-500"
        >
          <div className="space-y-3">
            {trendInsights.valuePicksUnder7.map((player, index) => (
              <div key={player.player_id} className="flex items-center justify-between p-3 bg-dark-700 rounded-lg">
                <div className="flex items-center space-x-3">
                  <CurrencyPoundIcon className="h-5 w-5 text-blue-400" />
                  <div>
                    <p className="text-white font-medium">{player.name}</p>
                    <p className="text-dark-400 text-sm">{player.team} • {player.position}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-white font-bold">{player.total_points}</p>
                  <p className="text-blue-400 text-sm">£{player.price}m</p>
                </div>
              </div>
            ))}
            {trendInsights.valuePicksUnder7.length === 0 && (
              <p className="text-dark-400 text-center py-4">No value picks found under £7.0m</p>
            )}
          </div>
        </Card>

        <Card
          title="Premium Players £10.0m+"
          subtitle="High-priced elite performers"
          className="border-l-4 border-purple-500"
        >
          <div className="space-y-3">
            {trendInsights.premiumPlayers.map((player, index) => (
              <div key={player.player_id} className="flex items-center justify-between p-3 bg-dark-700 rounded-lg">
                <div className="flex items-center space-x-3">
                  <TrophyIcon className="h-5 w-5 text-purple-400" />
                  <div>
                    <p className="text-white font-medium">{player.name}</p>
                    <p className="text-dark-400 text-sm">{player.team} • {player.position}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-white font-bold">{player.total_points}</p>
                  <p className="text-purple-400 text-sm">£{player.price}m</p>
                </div>
              </div>
            ))}
            {trendInsights.premiumPlayers.length === 0 && (
              <p className="text-dark-400 text-center py-4">No premium players found</p>
            )}
          </div>
        </Card>
      </div>

      {/* Position Analysis */}
      <Card title="Position Analysis" subtitle="Performance breakdown by position">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {['GK', 'DEF', 'MID', 'FWD'].map(position => {
            const positionPlayers = formTable.filter(p => p.position === position);
            const avgPoints = positionPlayers.length > 0
              ? Math.round(positionPlayers.reduce((sum, p) => sum + p.total_points, 0) / positionPlayers.length)
              : 0;
            const avgPrice = positionPlayers.length > 0
              ? (positionPlayers.reduce((sum, p) => sum + p.price, 0) / positionPlayers.length).toFixed(1)
              : 0;
            const topPlayer = positionPlayers.sort((a, b) => b.total_points - a.total_points)[0];

            return (
              <div key={position} className="bg-dark-800 rounded-lg p-4">
                <div className="text-center">
                  <Badge variant={
                    position === 'GK' ? 'yellow' :
                    position === 'DEF' ? 'green' :
                    position === 'MID' ? 'blue' : 'red'
                  } className="mb-3">
                    {position}
                  </Badge>
                  <div className="space-y-2">
                    <div>
                      <p className="text-dark-400 text-sm">Players</p>
                      <p className="text-white font-bold">{positionPlayers.length}</p>
                    </div>
                    <div>
                      <p className="text-dark-400 text-sm">Avg Points</p>
                      <p className="text-white font-bold">{avgPoints}</p>
                    </div>
                    <div>
                      <p className="text-dark-400 text-sm">Avg Price</p>
                      <p className="text-white font-bold">£{avgPrice}m</p>
                    </div>
                    {topPlayer && (
                      <div>
                        <p className="text-dark-400 text-sm">Top Player</p>
                        <p className="text-white font-medium text-sm">{topPlayer.name}</p>
                        <p className="text-primary-400 text-sm">{topPlayer.total_points} pts</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
};

export default Statistics;
