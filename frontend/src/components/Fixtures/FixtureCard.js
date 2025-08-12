import React from 'react';
import { ClockIcon, CalendarIcon } from '@heroicons/react/24/outline';
import TeamBadge from '../UI/TeamBadge';
import Badge from '../UI/Badge';

const FixtureCard = ({ fixture, size = 'md', className = '' }) => {
  if (!fixture) return null;

  const formatDate = (dateString) => {
    if (!dateString) return 'TBD';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  const formatTime = (dateString) => {
    if (!dateString) return 'Time TBD';
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const getDifficultyColor = (difficulty) => {
    if (difficulty <= 2) return 'text-green-400';
    if (difficulty === 3) return 'text-yellow-400';
    if (difficulty === 4) return 'text-orange-400';
    return 'text-red-400';
  };

  const getStatusBadge = () => {
    if (fixture.finished) {
      return <Badge variant="success" size="sm">FT</Badge>;
    }
    if (fixture.started) {
      return <Badge variant="warning" size="sm">LIVE</Badge>;
    }
    return <Badge variant="outline" size="sm">GW {fixture.event}</Badge>;
  };

  const homeTeam = fixture.team_home;
  const awayTeam = fixture.team_away;

  return (
    <div className={`bg-dark-800 rounded-lg p-4 border border-dark-700 hover:border-dark-600 transition-colors ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        {getStatusBadge()}
        <div className="flex items-center space-x-1 text-xs text-dark-400">
          <CalendarIcon className="h-3 w-3" />
          <span>{formatDate(fixture.kickoff_time)}</span>
        </div>
      </div>

      {/* Teams */}
      <div className="flex items-center justify-between mb-3">
        {/* Home Team */}
        <div className="flex flex-col items-center space-y-1 flex-1">
          <TeamBadge team={homeTeam} size="md" />
          <div className="text-center">
            <p className="text-white font-medium text-sm">{homeTeam?.short_name || 'TBD'}</p>
            <div className="flex items-center justify-center space-x-1">
              <span className="text-xs text-dark-400">H</span>
              <span className={`text-xs font-medium ${getDifficultyColor(fixture.team_h_difficulty)}`}>
                {fixture.team_h_difficulty}
              </span>
            </div>
          </div>
        </div>

        {/* VS and Score */}
        <div className="flex flex-col items-center space-y-1 px-4">
          {fixture.finished ? (
            <div className="text-center">
              <div className="text-lg font-bold text-white">
                {fixture.team_h_score} - {fixture.team_a_score}
              </div>
              <span className="text-xs text-dark-400">FT</span>
            </div>
          ) : fixture.started ? (
            <div className="text-center">
              <div className="text-lg font-bold text-white">
                {fixture.team_h_score || 0} - {fixture.team_a_score || 0}
              </div>
              <span className="text-xs text-warning-400">{fixture.minutes}'</span>
            </div>
          ) : (
            <div className="text-center">
              <span className="text-sm font-medium text-dark-400">VS</span>
              <div className="flex items-center space-x-1 text-xs text-dark-400">
                <ClockIcon className="h-3 w-3" />
                <span>{formatTime(fixture.kickoff_time)}</span>
              </div>
            </div>
          )}
        </div>

        {/* Away Team */}
        <div className="flex flex-col items-center space-y-1 flex-1">
          <TeamBadge team={awayTeam} size="md" />
          <div className="text-center">
            <p className="text-white font-medium text-sm">{awayTeam?.short_name || 'TBD'}</p>
            <div className="flex items-center justify-center space-x-1">
              <span className="text-xs text-dark-400">A</span>
              <span className={`text-xs font-medium ${getDifficultyColor(fixture.team_a_difficulty)}`}>
                {fixture.team_a_difficulty}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Additional Info */}
      {fixture.kickoff_time && (
        <div className="text-center pt-2 border-t border-dark-700">
          <p className="text-xs text-dark-400">
            {new Date(fixture.kickoff_time).toLocaleDateString('en-US', {
              weekday: 'long',
              month: 'long',
              day: 'numeric'
            })}
          </p>
        </div>
      )}
    </div>
  );
};

export default FixtureCard;
