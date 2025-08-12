import React, { useState, useMemo } from 'react';
import { useQuery } from 'react-query';
import {
  FunnelIcon,
  MagnifyingGlassIcon,
  ChartBarIcon,
  TrophyIcon,
  UserGroupIcon,
  CalendarDaysIcon
} from '@heroicons/react/24/outline';

import Card from '../components/UI/Card';
import Button from '../components/UI/Button';
import Badge from '../components/UI/Badge';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import TeamCard from '../components/Teams/TeamCard';
import TeamDetailModal from '../components/Teams/TeamDetailModal';
import TeamComparison from '../components/Teams/TeamComparison';

import { apiService } from '../services/apiService';

const Teams = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('name');
  const [filterStrength, setFilterStrength] = useState('all');
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [showComparison, setShowComparison] = useState(false);

  // Fetch teams
  const {
    data: teams,
    isLoading: loadingTeams,
    error: teamsError
  } = useQuery(
    'teams',
    () => apiService.getTeams(),
    {
      staleTime: 30 * 60 * 1000,
    }
  );

  // Fetch players for team analysis
  const {
    data: players,
    isLoading: loadingPlayers
  } = useQuery(
    'all-players',
    () => apiService.getPlayers({ limit: 1000 }), // Get all players
    {
      staleTime: 10 * 60 * 1000,
    }
  );

  // Fetch fixtures for team analysis
  const {
    data: fixtures,
    isLoading: loadingFixtures
  } = useQuery(
    'fixtures-all',
    () => apiService.getFixtures({ next_gameweeks: 10 }),
    {
      staleTime: 5 * 60 * 1000,
    }
  );

  // Process team data with players and fixtures
  const processedTeams = useMemo(() => {
    if (!teams || !players || !fixtures) return [];

    return teams.map(team => {
      const teamPlayers = players.filter(player => player.team_id === team.id);
      const teamFixtures = fixtures.filter(fixture =>
        fixture.team_h_id === team.id || fixture.team_a_id === team.id
      );

      // Calculate team stats
      const totalPoints = teamPlayers.reduce((sum, player) => sum + (player.total_points || 0), 0);
      const avgForm = teamPlayers.length > 0
        ? teamPlayers.reduce((sum, player) => sum + (parseFloat(player.form) || 0), 0) / teamPlayers.length
        : 0;

      return {
        ...team,
        players: teamPlayers,
        fixtures: teamFixtures,
        stats: {
          points: totalPoints,
          form: avgForm.toFixed(1),
          strength_overall_home: team.strength_overall_home || 0,
          strength_overall_away: team.strength_overall_away || 0,
          strength_attack_home: team.strength_attack_home || 0,
          strength_attack_away: team.strength_attack_away || 0,
          strength_defence_home: team.strength_defence_home || 0,
          strength_defence_away: team.strength_defence_away || 0,
        }
      };
    });
  }, [teams, players, fixtures]);

  // Filter and sort teams
  const filteredAndSortedTeams = useMemo(() => {
    let filtered = processedTeams.filter(team => {
      const matchesSearch = team.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           team.short_name.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesStrength = filterStrength === 'all' ||
        (filterStrength === 'strong' && (team.stats.strength_overall_home >= 4 || team.stats.strength_overall_away >= 4)) ||
        (filterStrength === 'weak' && (team.stats.strength_overall_home <= 2 && team.stats.strength_overall_away <= 2));

      return matchesSearch && matchesStrength;
    });

    // Sort teams
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'points':
          return (b.stats.points || 0) - (a.stats.points || 0);
        case 'form':
          return (parseFloat(b.stats.form) || 0) - (parseFloat(a.stats.form) || 0);
        case 'strength':
          return ((b.stats.strength_overall_home + b.stats.strength_overall_away) / 2) -
                 ((a.stats.strength_overall_home + a.stats.strength_overall_away) / 2);
        default:
          return 0;
      }
    });

    return filtered;
  }, [processedTeams, searchTerm, sortBy, filterStrength]);

  const handleTeamDetails = (team, tab = 'overview') => {
    setSelectedTeam({ ...team, activeTab: tab });
    setShowModal(true);
  };

  const isLoading = loadingTeams || loadingPlayers || loadingFixtures;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Teams</h1>
          <p className="text-dark-400 mt-1">
            Analyze team performance, squad strength, and fixture difficulty
          </p>
        </div>

        <Button
          variant="primary"
          onClick={() => setShowComparison(true)}
          icon={<ChartBarIcon className="h-4 w-4" />}
          disabled={processedTeams.length < 2}
        >
          Compare Teams
        </Button>
      </div>

      {/* Filters and Search */}
      <Card title="Team Analysis" subtitle="Filter and analyze Premier League teams">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-dark-400" />
            <input
              type="text"
              placeholder="Search teams..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10 w-full"
            />
          </div>

          {/* Sort */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="input w-full"
          >
            <option value="name">Sort by Name</option>
            <option value="points">Sort by Points</option>
            <option value="form">Sort by Form</option>
            <option value="strength">Sort by Strength</option>
          </select>

          {/* Strength Filter */}
          <select
            value={filterStrength}
            onChange={(e) => setFilterStrength(e.target.value)}
            className="input w-full"
          >
            <option value="all">All Teams</option>
            <option value="strong">Strong Teams</option>
            <option value="weak">Weak Teams</option>
          </select>

          {/* Clear Filters */}
          <Button
            variant="secondary"
            onClick={() => {
              setSearchTerm('');
              setSortBy('name');
              setFilterStrength('all');
            }}
            icon={<FunnelIcon className="h-4 w-4" />}
            disabled={!searchTerm && sortBy === 'name' && filterStrength === 'all'}
          >
            Clear Filters
          </Button>
        </div>

        {/* Active Filters */}
        {(searchTerm || sortBy !== 'name' || filterStrength !== 'all') && (
          <div className="flex items-center space-x-2 mt-4 pt-4 border-t border-dark-700">
            <span className="text-sm text-dark-400">Active filters:</span>
            {searchTerm && (
              <Badge variant="primary" size="sm">
                Search: "{searchTerm}"
              </Badge>
            )}
            {sortBy !== 'name' && (
              <Badge variant="primary" size="sm">
                Sort: {sortBy}
              </Badge>
            )}
            {filterStrength !== 'all' && (
              <Badge variant="primary" size="sm">
                {filterStrength === 'strong' ? 'Strong Teams' : 'Weak Teams'}
              </Badge>
            )}
          </div>
        )}
      </Card>

      {/* Quick Stats */}
      {!isLoading && processedTeams.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="text-center">
            <div className="flex items-center justify-center mb-2">
              <UserGroupIcon className="h-8 w-8 text-primary-500" />
            </div>
            <div className="text-2xl font-bold text-white">{processedTeams.length}</div>
            <div className="text-sm text-dark-400">Premier League Teams</div>
          </Card>

          <Card className="text-center">
            <div className="flex items-center justify-center mb-2">
              <TrophyIcon className="h-8 w-8 text-success-500" />
            </div>
            <div className="text-2xl font-bold text-white">
              {processedTeams.reduce((sum, team) => sum + team.players.length, 0)}
            </div>
            <div className="text-sm text-dark-400">Total Players</div>
          </Card>

          <Card className="text-center">
            <div className="flex items-center justify-center mb-2">
              <ChartBarIcon className="h-8 w-8 text-warning-500" />
            </div>
            <div className="text-2xl font-bold text-white">
              {Math.round(processedTeams.reduce((sum, team) => sum + team.stats.points, 0) / processedTeams.length)}
            </div>
            <div className="text-sm text-dark-400">Avg Team Points</div>
          </Card>

          <Card className="text-center">
            <div className="flex items-center justify-center mb-2">
              <CalendarDaysIcon className="h-8 w-8 text-info-500" />
            </div>
            <div className="text-2xl font-bold text-white">
              {fixtures ? fixtures.filter(f => !f.finished).length : 0}
            </div>
            <div className="text-sm text-dark-400">Upcoming Fixtures</div>
          </Card>
        </div>
      )}

      {/* Teams Grid */}
      {isLoading ? (
        <Card>
          <LoadingSpinner size="lg" text="Loading teams data..." />
        </Card>
      ) : teamsError ? (
        <Card title="Error" className="border-danger-700">
          <div className="text-center py-8">
            <p className="text-danger-400 mb-4">
              Failed to load teams: {teamsError.message}
            </p>
            <Button variant="primary" onClick={() => window.location.reload()}>
              Try Again
            </Button>
          </div>
        </Card>
      ) : filteredAndSortedTeams.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAndSortedTeams.map(team => (
            <TeamCard
              key={team.id}
              team={team}
              players={team.players}
              fixtures={team.fixtures}
              stats={team.stats}
              onViewDetails={handleTeamDetails}
            />
          ))}
        </div>
      ) : (
        <Card title="No Teams Found" subtitle="No teams match your current filters">
          <div className="text-center py-8">
            <UserGroupIcon className="h-12 w-12 text-dark-500 mx-auto mb-4" />
            <p className="text-dark-400 mb-4">
              No teams found matching your search criteria
            </p>
            <Button
              variant="primary"
              onClick={() => {
                setSearchTerm('');
                setSortBy('name');
                setFilterStrength('all');
              }}
            >
              Clear Filters
            </Button>
          </div>
        </Card>
      )}

      {/* Team Detail Modal */}
      <TeamDetailModal
        team={selectedTeam}
        players={selectedTeam?.players || []}
        fixtures={selectedTeam?.fixtures || []}
        stats={selectedTeam?.stats || {}}
        isOpen={showModal}
        onClose={() => {
          setShowModal(false);
          setSelectedTeam(null);
        }}
      />

      {/* Team Comparison Modal */}
      <TeamComparison
        teams={processedTeams.slice(0, 2)}
        allTeams={processedTeams}
        isOpen={showComparison}
        onClose={() => setShowComparison(false)}
      />
    </div>
  );
};

export default Teams;
