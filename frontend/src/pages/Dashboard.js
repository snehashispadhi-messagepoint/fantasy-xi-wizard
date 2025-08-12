import React from 'react';
import { useQuery } from 'react-query';
import { 
  ChartBarIcon, 
  UserGroupIcon, 
  CalendarDaysIcon,
  SparklesIcon,
  TrophyIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

import Card from '../components/UI/Card';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import Badge from '../components/UI/Badge';
import FixtureCard from '../components/Fixtures/FixtureCard';
import DataSync from '../components/Admin/DataSync';
import { useData } from '../context/DataContext';
import { apiService } from '../services/apiService';

const Dashboard = () => {
  const { currentGameweek, formattedDeadline } = useData();

  // Fetch dashboard data
  const { data: topPerformers, isLoading: loadingPerformers } = useQuery(
    'top-performers',
    () => apiService.getTopPerformers({ limit: 5 }),
    { staleTime: 5 * 60 * 1000 }
  );

  const { data: formTable, isLoading: loadingForm } = useQuery(
    'form-table',
    () => apiService.getFormTable(5),
    { staleTime: 5 * 60 * 1000 }
  );

  const { data: fixtures, isLoading: loadingFixtures } = useQuery(
    'upcoming-fixtures',
    () => apiService.getFixtures({ next_gameweeks: 1 }),
    { staleTime: 2 * 60 * 1000 }
  );

  const StatCard = ({ title, value, subtitle, icon: Icon, color = 'primary' }) => (
    <Card className="p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-dark-400">{title}</p>
          <p className="text-2xl font-bold text-white mt-1">{value}</p>
          {subtitle && (
            <p className="text-sm text-dark-500 mt-1">{subtitle}</p>
          )}
        </div>
        <div className={`p-3 rounded-lg bg-${color}-500 bg-opacity-20`}>
          <Icon className={`h-6 w-6 text-${color}-500`} />
        </div>
      </div>
    </Card>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-dark-400 mt-1">
            Welcome to Fantasy XI Wizard - Your AI-powered FPL companion
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <Badge variant="primary" size="lg">
            GW {currentGameweek || '--'}
          </Badge>
          {formattedDeadline && (
            <Badge variant="warning" size="lg">
              <ClockIcon className="h-4 w-4 mr-1" />
              {formattedDeadline}
            </Badge>
          )}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Current Gameweek"
          value={currentGameweek || '--'}
          subtitle="Premier League"
          icon={CalendarDaysIcon}
          color="primary"
        />
        <StatCard
          title="Next Deadline"
          value={formattedDeadline || 'TBD'}
          subtitle="Time remaining"
          icon={ClockIcon}
          color="warning"
        />
        <StatCard
          title="Top Scorer"
          value={topPerformers?.[0]?.name || '--'}
          subtitle={`${topPerformers?.[0]?.total_points || 0} points`}
          icon={TrophyIcon}
          color="success"
        />
        <StatCard
          title="AI Recommendations"
          value="Ready"
          subtitle="Get smart picks"
          icon={SparklesIcon}
          color="purple"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Performers */}
        <Card
          title="Top Performers"
          subtitle="Highest scoring players from 2024-25 season"
          className="lg:col-span-2"
        >
          {loadingPerformers ? (
            <LoadingSpinner text="Loading top performers..." />
          ) : (
            <div className="space-y-3">
              <div className="mb-3 p-3 bg-blue-900/20 border border-blue-700 rounded-lg">
                <p className="text-xs text-blue-300">
                  📊 Showing 2024-25 season data. Will update to current season after GW1 2025-26 is played.
                </p>
              </div>
              {topPerformers?.slice(0, 5).map((player, index) => (
                <div 
                  key={player.player_id} 
                  className="flex items-center justify-between p-3 bg-dark-800 rounded-lg hover:bg-dark-700 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                      {index + 1}
                    </div>
                    <div>
                      <p className="font-medium text-white">{player.name}</p>
                      <p className="text-sm text-dark-400">{player.team} • {player.position}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-white">{player.total_points}</p>
                    <p className="text-sm text-dark-400">points</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Form Table */}
        <Card title="In Form" subtitle="Best recent performers">
          {loadingForm ? (
            <LoadingSpinner text="Loading form data..." />
          ) : (
            <div className="space-y-3">
              {formTable?.slice(0, 5).map((player, index) => (
                <div 
                  key={player.player_id}
                  className="flex items-center justify-between"
                >
                  <div>
                    <p className="font-medium text-white text-sm">{player.name}</p>
                    <p className="text-xs text-dark-400">{player.team}</p>
                  </div>
                  <Badge variant="success" size="sm">
                    {player.form}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      {/* Upcoming Fixtures */}
      <Card title="Upcoming Fixtures" subtitle="Next gameweek matches">
        {loadingFixtures ? (
          <LoadingSpinner text="Loading fixtures..." />
        ) : fixtures && fixtures.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {fixtures.slice(0, 6).map((fixture) => (
              <FixtureCard
                key={fixture.id}
                fixture={fixture}
                size="md"
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <CalendarDaysIcon className="h-12 w-12 text-dark-500 mx-auto mb-4" />
            <p className="text-dark-400">No upcoming fixtures available</p>
          </div>
        )}
      </Card>

      {/* Live Data Management */}
      <DataSync showStats={true} compact={false} />

      {/* Quick Actions */}
      <Card title="Quick Actions" subtitle="Jump to key features">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="p-4 bg-dark-800 rounded-lg hover:bg-dark-700 transition-colors text-center">
            <UserGroupIcon className="h-8 w-8 text-primary-500 mx-auto mb-2" />
            <p className="text-white font-medium">Players</p>
            <p className="text-xs text-dark-400">Browse & analyze</p>
          </button>
          
          <button className="p-4 bg-dark-800 rounded-lg hover:bg-dark-700 transition-colors text-center">
            <ChartBarIcon className="h-8 w-8 text-success-500 mx-auto mb-2" />
            <p className="text-white font-medium">Statistics</p>
            <p className="text-xs text-dark-400">Deep insights</p>
          </button>
          
          <button className="p-4 bg-dark-800 rounded-lg hover:bg-dark-700 transition-colors text-center">
            <SparklesIcon className="h-8 w-8 text-purple-500 mx-auto mb-2" />
            <p className="text-white font-medium">AI Tips</p>
            <p className="text-xs text-dark-400">Smart recommendations</p>
          </button>
          
          <button className="p-4 bg-dark-800 rounded-lg hover:bg-dark-700 transition-colors text-center">
            <CalendarDaysIcon className="h-8 w-8 text-warning-500 mx-auto mb-2" />
            <p className="text-white font-medium">Fixtures</p>
            <p className="text-xs text-dark-400">Plan ahead</p>
          </button>
        </div>
      </Card>
    </div>
  );
};

export default Dashboard;
