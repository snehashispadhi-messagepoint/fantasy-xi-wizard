import React from 'react';
import { 
  UserGroupIcon,
  TrophyIcon,
  ChartBarIcon,
  CalendarDaysIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';

import Card from '../UI/Card';
import Button from '../UI/Button';
import Badge from '../UI/Badge';
import TeamBadge from '../UI/TeamBadge';

const TeamCard = ({ 
  team, 
  players = [], 
  fixtures = [], 
  stats = {},
  onViewDetails,
  className = '' 
}) => {
  if (!team) return null;

  const getFormBadge = (form) => {
    if (!form || form === 0) return { variant: 'outline', text: 'N/A' };
    if (form >= 4) return { variant: 'success', text: 'Excellent' };
    if (form >= 3) return { variant: 'primary', text: 'Good' };
    if (form >= 2) return { variant: 'warning', text: 'Average' };
    return { variant: 'danger', text: 'Poor' };
  };

  const getStrengthColor = (strength) => {
    if (strength >= 4) return 'text-green-400';
    if (strength >= 3) return 'text-yellow-400';
    if (strength >= 2) return 'text-orange-400';
    return 'text-red-400';
  };

  const upcomingFixtures = fixtures.filter(f => !f.finished).slice(0, 3);
  const topPlayers = players
    .sort((a, b) => (b.total_points || 0) - (a.total_points || 0))
    .slice(0, 3);

  const formBadge = getFormBadge(stats.form);

  return (
    <Card className={`hover:border-primary-600 transition-colors ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <TeamBadge team={team} size="lg" />
          <div>
            <h3 className="text-lg font-bold text-white">{team.name}</h3>
            <p className="text-sm text-dark-400">{team.short_name}</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Badge variant={formBadge.variant} size="sm">
            {formBadge.text}
          </Badge>
          {stats.position && (
            <Badge variant="outline" size="sm">
              #{stats.position}
            </Badge>
          )}
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div className="text-center">
          <div className="text-lg font-bold text-white">
            {players.length}
          </div>
          <div className="text-xs text-dark-400">Players</div>
        </div>
        
        <div className="text-center">
          <div className="text-lg font-bold text-white">
            {stats.points || 0}
          </div>
          <div className="text-xs text-dark-400">Points</div>
        </div>
        
        <div className="text-center">
          <div className={`text-lg font-bold ${getStrengthColor(stats.strength_overall_home || 0)}`}>
            {stats.strength_overall_home || 0}
          </div>
          <div className="text-xs text-dark-400">Home</div>
        </div>
        
        <div className="text-center">
          <div className={`text-lg font-bold ${getStrengthColor(stats.strength_overall_away || 0)}`}>
            {stats.strength_overall_away || 0}
          </div>
          <div className="text-xs text-dark-400">Away</div>
        </div>
      </div>

      {/* Top Players */}
      {topPlayers.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center space-x-2 mb-2">
            <TrophyIcon className="h-4 w-4 text-primary-500" />
            <h4 className="text-sm font-medium text-white">Top Players</h4>
          </div>
          <div className="space-y-2">
            {topPlayers.map((player, index) => (
              <div key={player.id} className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-2">
                  <span className="w-5 h-5 bg-primary-600 rounded-full flex items-center justify-center text-xs text-white font-bold">
                    {index + 1}
                  </span>
                  <span className="text-white">{player.web_name}</span>
                  <Badge variant="outline" size="xs">
                    {player.element_type === 1 ? 'GK' : 
                     player.element_type === 2 ? 'DEF' : 
                     player.element_type === 3 ? 'MID' : 'FWD'}
                  </Badge>
                </div>
                <div className="text-primary-400 font-medium">
                  {player.total_points || 0} pts
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upcoming Fixtures */}
      {upcomingFixtures.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center space-x-2 mb-2">
            <CalendarDaysIcon className="h-4 w-4 text-primary-500" />
            <h4 className="text-sm font-medium text-white">Next Fixtures</h4>
          </div>
          <div className="space-y-1">
            {upcomingFixtures.map((fixture) => {
              const isHome = fixture.team_h_id === team.id;
              const opponent = isHome ? fixture.team_away : fixture.team_home;
              const difficulty = isHome ? fixture.team_h_difficulty : fixture.team_a_difficulty;
              
              return (
                <div key={fixture.id} className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2">
                    <span className="text-dark-400">GW{fixture.event}</span>
                    <span className="text-white">
                      {isHome ? 'vs' : '@'} {opponent?.short_name || 'TBD'}
                    </span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <span className={`text-xs font-medium ${
                      difficulty <= 2 ? 'text-green-400' :
                      difficulty === 3 ? 'text-yellow-400' :
                      difficulty === 4 ? 'text-orange-400' : 'text-red-400'
                    }`}>
                      {difficulty}
                    </span>
                    <span className="text-xs text-dark-400">
                      {isHome ? '(H)' : '(A)'}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex space-x-2 pt-4 border-t border-dark-700">
        <Button
          variant="primary"
          size="sm"
          onClick={() => onViewDetails?.(team)}
          icon={<ArrowRightIcon className="h-4 w-4" />}
          className="flex-1"
        >
          View Details
        </Button>
        
        <Button
          variant="secondary"
          size="sm"
          icon={<UserGroupIcon className="h-4 w-4" />}
          onClick={() => onViewDetails?.(team, 'squad')}
        >
          Squad
        </Button>
        
        <Button
          variant="secondary"
          size="sm"
          icon={<ChartBarIcon className="h-4 w-4" />}
          onClick={() => onViewDetails?.(team, 'stats')}
        >
          Stats
        </Button>
      </div>
    </Card>
  );
};

export default TeamCard;
