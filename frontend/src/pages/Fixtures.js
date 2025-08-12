import React, { useState } from 'react';
import { useQuery } from 'react-query';
import {
  CalendarDaysIcon,
  FunnelIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

import Card from '../components/UI/Card';
import Button from '../components/UI/Button';
import Badge from '../components/UI/Badge';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import FixtureCard from '../components/Fixtures/FixtureCard';

import { apiService } from '../services/apiService';

const Fixtures = () => {
  const [selectedGameweek, setSelectedGameweek] = useState(null);

  // Fetch fixtures
  const {
    data: fixtures,
    isLoading: loadingFixtures,
    error: fixturesError
  } = useQuery(
    ['fixtures', selectedGameweek],
    () => apiService.getFixtures({
      gameweek: selectedGameweek,
      next_gameweeks: selectedGameweek ? 1 : 5
    }),
    {
      staleTime: 5 * 60 * 1000,
    }
  );

  const gameweeks = Array.from({ length: 38 }, (_, i) => i + 1);

  const getFixturesByGameweek = () => {
    if (!fixtures) return {};

    return fixtures.reduce((acc, fixture) => {
      const gw = fixture.event;
      if (!acc[gw]) acc[gw] = [];
      acc[gw].push(fixture);
      return acc;
    }, {});
  };

  const fixturesByGameweek = getFixturesByGameweek();
  const gameweekNumbers = Object.keys(fixturesByGameweek).sort((a, b) => a - b);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Fixtures</h1>
        <p className="text-dark-400 mt-1">
          Premier League fixtures with team badges and difficulty ratings
        </p>
      </div>

      {/* Gameweek Filter */}
      <Card title="Filter by Gameweek" subtitle="Select a specific gameweek or view upcoming fixtures">
        <div className="flex items-center space-x-4">
          <select
            value={selectedGameweek || ''}
            onChange={(e) => setSelectedGameweek(e.target.value ? parseInt(e.target.value) : null)}
            className="input flex-1 max-w-xs"
          >
            <option value="">Next 5 Gameweeks</option>
            {gameweeks.map(gw => (
              <option key={gw} value={gw}>Gameweek {gw}</option>
            ))}
          </select>

          {selectedGameweek && (
            <Button
              variant="secondary"
              onClick={() => setSelectedGameweek(null)}
              icon={<FunnelIcon className="h-4 w-4" />}
            >
              Clear Filter
            </Button>
          )}
        </div>
      </Card>

      {/* Fixtures */}
      {loadingFixtures ? (
        <Card>
          <LoadingSpinner size="lg" text="Loading fixtures..." />
        </Card>
      ) : fixturesError ? (
        <Card title="Error" className="border-danger-700">
          <div className="text-center py-8">
            <p className="text-danger-400 mb-4">
              Failed to load fixtures: {fixturesError.message}
            </p>
            <Button variant="primary" onClick={() => window.location.reload()}>
              Try Again
            </Button>
          </div>
        </Card>
      ) : fixtures && fixtures.length > 0 ? (
        <div className="space-y-6">
          {gameweekNumbers.map(gameweek => (
            <Card
              key={gameweek}
              title={`Gameweek ${gameweek}`}
              subtitle={`${fixturesByGameweek[gameweek].length} fixtures`}
            >
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {fixturesByGameweek[gameweek].map(fixture => (
                  <FixtureCard
                    key={fixture.id}
                    fixture={fixture}
                    size="md"
                  />
                ))}
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card title="No Fixtures" subtitle="No fixtures found">
          <div className="text-center py-8">
            <CalendarDaysIcon className="h-12 w-12 text-dark-500 mx-auto mb-4" />
            <p className="text-dark-400">No fixtures available for the selected criteria</p>
          </div>
        </Card>
      )}

      {/* Legend */}
      <Card title="Fixture Difficulty Legend" subtitle="Understanding fixture difficulty ratings">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {[
            { rating: 1, label: 'Very Easy', color: 'text-green-400' },
            { rating: 2, label: 'Easy', color: 'text-green-400' },
            { rating: 3, label: 'Average', color: 'text-yellow-400' },
            { rating: 4, label: 'Hard', color: 'text-orange-400' },
            { rating: 5, label: 'Very Hard', color: 'text-red-400' }
          ].map(({ rating, label, color }) => (
            <div key={rating} className="text-center">
              <div className={`text-lg font-bold ${color} mb-1`}>
                {rating}
              </div>
              <p className="text-sm text-dark-400">{label}</p>
            </div>
          ))}
        </div>

        <div className="mt-4 pt-4 border-t border-dark-700">
          <div className="flex items-center justify-center space-x-4 text-xs text-dark-400">
            <div className="flex items-center space-x-1">
              <span className="w-2 h-2 bg-green-400 rounded-full"></span>
              <span>H = Home</span>
            </div>
            <div className="flex items-center space-x-1">
              <span className="w-2 h-2 bg-blue-400 rounded-full"></span>
              <span>A = Away</span>
            </div>
            <div className="flex items-center space-x-1">
              <ClockIcon className="h-3 w-3" />
              <span>Kickoff times in local timezone</span>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default Fixtures;
