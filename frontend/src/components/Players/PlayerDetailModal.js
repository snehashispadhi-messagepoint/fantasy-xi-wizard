import React, { useState, useEffect } from 'react';
import {
  XMarkIcon,
  ChartBarIcon,
  TrophyIcon,
  CurrencyPoundIcon,
  UserIcon,
  CalendarDaysIcon,
  FireIcon,
  HomeIcon,
  MapPinIcon
} from '@heroicons/react/24/outline';

import Button from '../UI/Button';
import Badge from '../UI/Badge';
import TeamBadge from '../UI/TeamBadge';
import LoadingSpinner from '../UI/LoadingSpinner';
import { apiService } from '../../services/apiService';

const PlayerDetailModal = ({
  player,
  isOpen,
  onClose
}) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [fixtures, setFixtures] = useState([]);
  const [loadingFixtures, setLoadingFixtures] = useState(false);

  // Fetch fixtures when modal opens and player changes
  useEffect(() => {
    if (isOpen && player && player.team) {
      fetchUpcomingFixtures();
    }
  }, [isOpen, player]);

  const fetchUpcomingFixtures = async () => {
    if (!player?.team?.id) return;

    setLoadingFixtures(true);
    try {
      const fixtures = await apiService.getFixtures({
        team_id: player.team.id,
        next_gameweeks: 5
      });
      setFixtures(fixtures || []);
    } catch (error) {
      console.error('Error fetching fixtures:', error);
      setFixtures([]);
    } finally {
      setLoadingFixtures(false);
    }
  };

  if (!isOpen || !player) return null;

  const tabs = [
    { id: 'overview', label: 'Overview', icon: UserIcon },
    { id: 'stats', label: 'Statistics', icon: ChartBarIcon },
    { id: 'form', label: 'Form & Fixtures', icon: CalendarDaysIcon }
  ];

  const getPositionName = (elementType) => {
    const positions = {
      1: 'Goalkeeper',
      2: 'Defender', 
      3: 'Midfielder',
      4: 'Forward'
    };
    return positions[elementType] || 'Unknown';
  };

  const getPositionColor = (elementType) => {
    const colors = {
      1: 'bg-yellow-500', // Goalkeeper
      2: 'bg-green-500',  // Defender
      3: 'bg-blue-500',   // Midfielder
      4: 'bg-red-500'     // Forward
    };
    return colors[elementType] || 'bg-gray-500';
  };

  const formatPrice = (cost) => {
    return (cost / 10).toFixed(1);
  };

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Player Header */}
      <div className="flex items-center space-x-4">
        <div className={`w-16 h-16 ${getPositionColor(player.element_type)} rounded-full flex items-center justify-center`}>
          <span className="text-white text-lg font-bold">
            {getPositionName(player.element_type).charAt(0)}
          </span>
        </div>
        <div className="flex-1">
          <h2 className="text-2xl font-bold text-white">{player.web_name}</h2>
          <p className="text-dark-400">{player.first_name} {player.second_name}</p>
          <div className="flex items-center space-x-2 mt-2">
            <Badge variant="primary">{getPositionName(player.element_type)}</Badge>
            <Badge variant="outline">£{formatPrice(player.now_cost)}m</Badge>
            {player.team && (
              <div className="flex items-center space-x-1">
                <TeamBadge team={player.team} size="sm" />
                <span className="text-sm text-dark-400">{player.team.name}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Quick Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-dark-800 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-white">{player.total_points || 0}</div>
          <div className="text-sm text-dark-400">Total Points</div>
        </div>
        <div className="bg-dark-800 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-green-400">£{formatPrice(player.now_cost)}</div>
          <div className="text-sm text-dark-400">Price</div>
        </div>
        <div className="bg-dark-800 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-blue-400">{player.selected_by_percent || 0}%</div>
          <div className="text-sm text-dark-400">Ownership</div>
        </div>
        <div className="bg-dark-800 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-yellow-400">{player.form || 0}</div>
          <div className="text-sm text-dark-400">Form</div>
        </div>
      </div>

      {/* Player Info */}
      <div className="bg-dark-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Player Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-dark-400">Status</p>
            <p className="text-white font-medium">{player.status || 'Available'}</p>
          </div>
          <div>
            <p className="text-sm text-dark-400">News</p>
            <p className="text-white font-medium">{player.news || 'No recent news'}</p>
          </div>
          <div>
            <p className="text-sm text-dark-400">Points per Game</p>
            <p className="text-white font-medium">{player.points_per_game || 0}</p>
          </div>
          <div>
            <p className="text-sm text-dark-400">Transfers In (GW)</p>
            <p className="text-white font-medium">{player.transfers_in_event || 0}</p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderStats = () => (
    <div className="space-y-6">
      {/* Attacking Stats */}
      <div className="bg-dark-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
          <TrophyIcon className="h-5 w-5 mr-2" />
          Attacking Stats
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-xl font-bold text-white">{player.goals_scored || 0}</div>
            <div className="text-sm text-dark-400">Goals</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-white">{player.assists || 0}</div>
            <div className="text-sm text-dark-400">Assists</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-white">{player.expected_goals || 0}</div>
            <div className="text-sm text-dark-400">xG</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-white">{player.expected_assists || 0}</div>
            <div className="text-sm text-dark-400">xA</div>
          </div>
        </div>
      </div>

      {/* Defensive Stats */}
      <div className="bg-dark-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Defensive Stats</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-xl font-bold text-white">{player.clean_sheets || 0}</div>
            <div className="text-sm text-dark-400">Clean Sheets</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-white">{player.goals_conceded || 0}</div>
            <div className="text-sm text-dark-400">Goals Conceded</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-white">{player.saves || 0}</div>
            <div className="text-sm text-dark-400">Saves</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-white">{player.penalties_saved || 0}</div>
            <div className="text-sm text-dark-400">Penalties Saved</div>
          </div>
        </div>
      </div>

      {/* Bonus & Discipline */}
      <div className="bg-dark-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Bonus & Discipline</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-xl font-bold text-white">{player.bonus || 0}</div>
            <div className="text-sm text-dark-400">Bonus Points</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-white">{player.bps || 0}</div>
            <div className="text-sm text-dark-400">BPS</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-yellow-400">{player.yellow_cards || 0}</div>
            <div className="text-sm text-dark-400">Yellow Cards</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-red-400">{player.red_cards || 0}</div>
            <div className="text-sm text-dark-400">Red Cards</div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderForm = () => (
    <div className="space-y-6">
      {/* Form Analysis */}
      <div className="bg-dark-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
          <FireIcon className="h-5 w-5 mr-2" />
          Recent Form
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-white">{player.form || 0}</div>
            <div className="text-sm text-dark-400">Form (5 GWs)</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-white">{player.points_per_game || 0}</div>
            <div className="text-sm text-dark-400">Points per Game</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-white">{player.minutes || 0}</div>
            <div className="text-sm text-dark-400">Total Minutes</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-white">{player.starts || 0}</div>
            <div className="text-sm text-dark-400">Starts</div>
          </div>
        </div>
      </div>

      {/* Upcoming Fixtures */}
      <div className="bg-dark-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
          <CalendarDaysIcon className="h-5 w-5 mr-2" />
          Upcoming Fixtures
        </h3>

        {loadingFixtures ? (
          <div className="text-center py-8">
            <LoadingSpinner size="md" text="Loading fixtures..." />
          </div>
        ) : fixtures.length > 0 ? (
          <div className="space-y-3">
            {fixtures.slice(0, 5).map((fixture, index) => {
              const isHome = fixture.team_h_id === player.team?.id;
              const opponent = isHome ? fixture.team_away : fixture.team_home;
              const difficulty = isHome ? fixture.team_h_difficulty : fixture.team_a_difficulty;

              const getDifficultyColor = (diff) => {
                if (diff <= 2) return 'bg-green-500';
                if (diff === 3) return 'bg-yellow-500';
                if (diff === 4) return 'bg-orange-500';
                return 'bg-red-500';
              };

              const formatKickoffTime = (kickoffTime) => {
                if (!kickoffTime) return 'TBD';
                const date = new Date(kickoffTime);
                return date.toLocaleDateString('en-GB', {
                  weekday: 'short',
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                });
              };

              return (
                <div key={fixture.id} className="flex items-center justify-between p-3 bg-dark-700 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="text-center">
                      <div className="text-xs text-dark-400">GW</div>
                      <div className="text-sm font-bold text-white">{fixture.event}</div>
                    </div>

                    <div className="flex items-center space-x-2">
                      {isHome ? (
                        <HomeIcon className="h-4 w-4 text-green-400" title="Home" />
                      ) : (
                        <MapPinIcon className="h-4 w-4 text-blue-400" title="Away" />
                      )}
                      <span className="text-white font-medium">
                        {isHome ? 'vs' : '@'} {opponent?.name || 'TBD'}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className="text-right">
                      <div className="text-xs text-dark-400">Kickoff</div>
                      <div className="text-sm text-white">{formatKickoffTime(fixture.kickoff_time)}</div>
                    </div>

                    <div className={`w-6 h-6 ${getDifficultyColor(difficulty)} rounded-full flex items-center justify-center`}>
                      <span className="text-white text-xs font-bold">{difficulty}</span>
                    </div>
                  </div>
                </div>
              );
            })}

            {fixtures.length > 5 && (
              <div className="text-center pt-2">
                <p className="text-sm text-dark-400">
                  Showing next 5 fixtures • {fixtures.length} total upcoming
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-8">
            <CalendarDaysIcon className="h-12 w-12 text-dark-500 mx-auto mb-4" />
            <p className="text-dark-400">No upcoming fixtures found</p>
          </div>
        )}
      </div>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview': return renderOverview();
      case 'stats': return renderStats();
      case 'form': return renderForm();
      default: return renderOverview();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-dark-900 rounded-xl border border-dark-700 w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-dark-700">
          <div className="flex items-center space-x-3">
            <div className={`w-10 h-10 ${getPositionColor(player.element_type)} rounded-full flex items-center justify-center`}>
              <span className="text-white text-sm font-bold">
                {getPositionName(player.element_type).charAt(0)}
              </span>
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">{player.web_name}</h2>
              <p className="text-sm text-dark-400">{player.team?.name}</p>
            </div>
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
        <div className="flex border-b border-dark-700">
          {tabs.map(tab => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'text-primary-400 border-b-2 border-primary-400 bg-dark-800'
                    : 'text-dark-400 hover:text-white hover:bg-dark-800'
                }`}
              >
                <div className="flex items-center justify-center space-x-2">
                  <Icon className="h-4 w-4" />
                  <span>{tab.label}</span>
                </div>
              </button>
            );
          })}
        </div>

        {/* Content */}
        <div className="p-6 max-h-[60vh] overflow-y-auto">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
};

export default PlayerDetailModal;
