import React, { useState } from 'react';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  ArrowsRightLeftIcon
} from '@heroicons/react/24/outline';
import { useQuery } from 'react-query';

import Card from '../components/UI/Card';
import Button from '../components/UI/Button';
import Badge from '../components/UI/Badge';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import PlayerComparison from '../components/Players/PlayerComparison';

import { useData } from '../context/DataContext';
import { apiService } from '../services/apiService';

const PlayerComparisonPage = () => {
  const { selectedPlayers, addSelectedPlayer, removeSelectedPlayer } = useData();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  // Search for players to add to comparison
  const handleSearch = async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      const results = await apiService.searchPlayers(query, 10);
      setSearchResults(results || []);
    } catch (error) {
      console.error('Search failed:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleAddPlayer = (player) => {
    addSelectedPlayer(player);
    setSearchQuery('');
    setSearchResults([]);
  };

  const handleRemovePlayer = (playerId) => {
    removeSelectedPlayer(playerId);
  };

  const isPlayerSelected = (playerId) => {
    return selectedPlayers.some(p => p.id === playerId);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Player Comparison</h1>
        <p className="text-dark-400 mt-1">
          Compare players side-by-side with detailed metrics and visualizations
        </p>
      </div>

      {/* Add Players Section */}
      <Card title="Add Players to Compare" subtitle="Search and select players for comparison">
        <div className="space-y-4">
          {/* Search Bar */}
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-dark-400" />
            </div>
            <input
              type="text"
              placeholder="Search for players to add..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                handleSearch(e.target.value);
              }}
              className="input pl-10 w-full"
            />
          </div>

          {/* Search Results */}
          {isSearching && (
            <div className="flex justify-center py-4">
              <LoadingSpinner size="sm" text="Searching..." />
            </div>
          )}

          {searchResults.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-white">Search Results:</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                {searchResults.map(player => (
                  <div
                    key={player.id}
                    className="flex items-center justify-between p-3 bg-dark-800 rounded-lg"
                  >
                    <div className="flex-1">
                      <p className="font-medium text-white text-sm">{player.web_name}</p>
                      <p className="text-xs text-dark-400">
                        {player.team?.name} • £{(player.now_cost / 10).toFixed(1)}m
                      </p>
                    </div>
                    <Button
                      variant={isPlayerSelected(player.id) ? "success" : "primary"}
                      size="sm"
                      onClick={() => handleAddPlayer(player)}
                      disabled={isPlayerSelected(player.id)}
                      icon={<PlusIcon className="h-4 w-4" />}
                    >
                      {isPlayerSelected(player.id) ? 'Added' : 'Add'}
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Current Selection Summary */}
          {selectedPlayers.length > 0 && (
            <div className="pt-4 border-t border-dark-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Badge variant="primary" size="lg">
                    {selectedPlayers.length} Selected
                  </Badge>
                  <span className="text-dark-400 text-sm">
                    {selectedPlayers.map(p => p.web_name).join(', ')}
                  </span>
                </div>
                {selectedPlayers.length >= 2 && (
                  <div className="flex items-center space-x-1 text-success-500">
                    <ArrowsRightLeftIcon className="h-4 w-4" />
                    <span className="text-sm">Ready to compare</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* Comparison Component */}
      <PlayerComparison
        players={selectedPlayers}
        onRemovePlayer={handleRemovePlayer}
      />
    </div>
  );
};

export default PlayerComparisonPage;
