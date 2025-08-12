import React, { useState } from 'react';
import { 
  XMarkIcon,
  UserGroupIcon,
  ChartBarIcon,
  CalendarDaysIcon,
  TrophyIcon,
  HomeIcon,
  MapPinIcon
} from '@heroicons/react/24/outline';

import Button from '../UI/Button';
import Badge from '../UI/Badge';
import TeamBadge from '../UI/TeamBadge';
import FixtureCard from '../Fixtures/FixtureCard';

const TeamDetailModal = ({ 
  team, 
  players = [], 
  fixtures = [], 
  stats = {},
  isOpen, 
  onClose 
}) => {
  const [activeTab, setActiveTab] = useState('overview');

  if (!isOpen || !team) return null;

  const tabs = [
    { id: 'overview', label: 'Overview', icon: HomeIcon },
    { id: 'squad', label: 'Squad', icon: UserGroupIcon },
    { id: 'fixtures', label: 'Fixtures', icon: CalendarDaysIcon },
    { id: 'stats', label: 'Statistics', icon: ChartBarIcon }
  ];

  const getPositionPlayers = (position) => {
    return players.filter(player => {
      switch (position) {
        case 'GK': return player.element_type === 1;
        case 'DEF': return player.element_type === 2;
        case 'MID': return player.element_type === 3;
        case 'FWD': return player.element_type === 4;
        default: return false;
      }
    }).sort((a, b) => (b.total_points || 0) - (a.total_points || 0));
  };

  const upcomingFixtures = fixtures.filter(f => !f.finished).slice(0, 5);
  const recentFixtures = fixtures.filter(f => f.finished).slice(0, 5);

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Team Header */}
      <div className="flex items-center space-x-4">
        <TeamBadge team={team} size="xl" />
        <div>
          <h2 className="text-2xl font-bold text-white">{team.name}</h2>
          <p className="text-dark-400">{team.short_name}</p>
          <div className="flex items-center space-x-2 mt-2">
            <Badge variant="primary">Premier League</Badge>
            {stats.position && (
              <Badge variant="outline">Position: #{stats.position}</Badge>
            )}
          </div>
        </div>
      </div>

      {/* Quick Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-dark-800 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-white">{players.length}</div>
          <div className="text-sm text-dark-400">Squad Size</div>
        </div>
        <div className="bg-dark-800 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-white">{stats.points || 0}</div>
          <div className="text-sm text-dark-400">Total Points</div>
        </div>
        <div className="bg-dark-800 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-green-400">{stats.strength_overall_home || 0}</div>
          <div className="text-sm text-dark-400">Home Strength</div>
        </div>
        <div className="bg-dark-800 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-blue-400">{stats.strength_overall_away || 0}</div>
          <div className="text-sm text-dark-400">Away Strength</div>
        </div>
      </div>

      {/* Top Performers */}
      <div className="bg-dark-800 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
          <TrophyIcon className="h-5 w-5 text-primary-500 mr-2" />
          Top Performers
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {players
            .sort((a, b) => (b.total_points || 0) - (a.total_points || 0))
            .slice(0, 6)
            .map((player, index) => (
              <div key={player.id} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className="w-6 h-6 bg-primary-600 rounded-full flex items-center justify-center text-xs text-white font-bold">
                    {index + 1}
                  </span>
                  <div>
                    <p className="text-white font-medium">{player.web_name}</p>
                    <p className="text-xs text-dark-400">
                      {player.element_type === 1 ? 'Goalkeeper' : 
                       player.element_type === 2 ? 'Defender' : 
                       player.element_type === 3 ? 'Midfielder' : 'Forward'}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-primary-400 font-bold">{player.total_points || 0}</p>
                  <p className="text-xs text-dark-400">points</p>
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );

  const renderSquad = () => (
    <div className="space-y-6">
      {['GK', 'DEF', 'MID', 'FWD'].map(position => {
        const positionPlayers = getPositionPlayers(position);
        const positionName = {
          'GK': 'Goalkeepers',
          'DEF': 'Defenders', 
          'MID': 'Midfielders',
          'FWD': 'Forwards'
        }[position];

        return (
          <div key={position} className="bg-dark-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-white mb-4">
              {positionName} ({positionPlayers.length})
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {positionPlayers.map(player => (
                <div key={player.id} className="flex items-center justify-between p-3 bg-dark-700 rounded-lg">
                  <div>
                    <p className="text-white font-medium">{player.web_name}</p>
                    <p className="text-sm text-dark-400">£{player.now_cost / 10}m</p>
                  </div>
                  <div className="text-right">
                    <p className="text-primary-400 font-bold">{player.total_points || 0}</p>
                    <p className="text-xs text-dark-400">points</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );

  const renderFixtures = () => (
    <div className="space-y-6">
      {/* Upcoming Fixtures */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">Upcoming Fixtures</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {upcomingFixtures.map(fixture => (
            <FixtureCard key={fixture.id} fixture={fixture} size="sm" />
          ))}
        </div>
      </div>

      {/* Recent Results */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">Recent Results</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {recentFixtures.map(fixture => (
            <FixtureCard key={fixture.id} fixture={fixture} size="sm" />
          ))}
        </div>
      </div>
    </div>
  );

  const renderStats = () => (
    <div className="space-y-6">
      {/* Strength Ratings */}
      <div className="bg-dark-800 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-white mb-4">Strength Ratings</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-xl font-bold text-green-400">{stats.strength_overall_home || 0}</div>
            <div className="text-sm text-dark-400">Overall Home</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-blue-400">{stats.strength_overall_away || 0}</div>
            <div className="text-sm text-dark-400">Overall Away</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-green-400">{stats.strength_attack_home || 0}</div>
            <div className="text-sm text-dark-400">Attack Home</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-blue-400">{stats.strength_attack_away || 0}</div>
            <div className="text-sm text-dark-400">Attack Away</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-green-400">{stats.strength_defence_home || 0}</div>
            <div className="text-sm text-dark-400">Defence Home</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-blue-400">{stats.strength_defence_away || 0}</div>
            <div className="text-sm text-dark-400">Defence Away</div>
          </div>
        </div>
      </div>

      {/* Additional Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-dark-800 rounded-lg p-4">
          <h4 className="text-md font-semibold text-white mb-3">Season Stats</h4>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-dark-400">Total Points</span>
              <span className="text-white font-medium">{stats.points || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-dark-400">Form</span>
              <span className="text-white font-medium">{stats.form || 'N/A'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-dark-400">Position</span>
              <span className="text-white font-medium">#{stats.position || 'N/A'}</span>
            </div>
          </div>
        </div>

        <div className="bg-dark-800 rounded-lg p-4">
          <h4 className="text-md font-semibold text-white mb-3">Squad Value</h4>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-dark-400">Total Value</span>
              <span className="text-white font-medium">
                £{(players.reduce((sum, p) => sum + (p.now_cost || 0), 0) / 10).toFixed(1)}m
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-dark-400">Average Price</span>
              <span className="text-white font-medium">
                £{players.length ? (players.reduce((sum, p) => sum + (p.now_cost || 0), 0) / 10 / players.length).toFixed(1) : 0}m
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-dark-400">Squad Size</span>
              <span className="text-white font-medium">{players.length}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview': return renderOverview();
      case 'squad': return renderSquad();
      case 'fixtures': return renderFixtures();
      case 'stats': return renderStats();
      default: return renderOverview();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-dark-900 rounded-xl border border-dark-700 w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-dark-700">
          <div className="flex items-center space-x-3">
            <TeamBadge team={team} size="md" />
            <h2 className="text-xl font-bold text-white">{team.name}</h2>
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

        {/* Tabs */}
        <div className="border-b border-dark-700">
          <nav className="flex space-x-8 px-6">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-500'
                      : 'border-transparent text-dark-400 hover:text-dark-300 hover:border-dark-600'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
};

export default TeamDetailModal;
