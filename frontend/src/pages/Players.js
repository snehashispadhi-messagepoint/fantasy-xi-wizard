import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import {
  Squares2X2Icon,
  TableCellsIcon,
  ArrowsRightLeftIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

import Card from '../components/UI/Card';
import Button from '../components/UI/Button';
import Badge from '../components/UI/Badge';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import PlayerFilters from '../components/Players/PlayerFilters';
import PlayerCard from '../components/Players/PlayerCard';
import PlayerTable from '../components/Players/PlayerTable';
import PlayerStats from '../components/Players/PlayerStats';
import PlayerDetailModal from '../components/Players/PlayerDetailModal';

import { useData } from '../context/DataContext';
import { apiService } from '../services/apiService';

const Players = () => {
  const { selectedPlayers, clearSelectedPlayers } = useData();
  const [viewMode, setViewMode] = useState('cards'); // 'cards' or 'table'
  const [searchQuery, setSearchQuery] = useState('');
  const [appliedFilters, setAppliedFilters] = useState({});
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [showPlayerModal, setShowPlayerModal] = useState(false);
  const playersPerPage = 20;

  // Fetch players with filters
  const {
    data: playersData,
    isLoading,
    error,
    refetch
  } = useQuery(
    ['players', appliedFilters, searchQuery, currentPage],
    () => {
      const params = {
        skip: (currentPage - 1) * playersPerPage,
        limit: playersPerPage,
        ...appliedFilters
      };

      if (searchQuery) {
        return apiService.searchPlayers(searchQuery, playersPerPage);
      }

      return apiService.getPlayers(params);
    },
    {
      keepPreviousData: true,
      staleTime: 2 * 60 * 1000, // 2 minutes
    }
  );

  const handleFiltersChange = (newFilters) => {
    setAppliedFilters(newFilters);
    setCurrentPage(1); // Reset to first page when filters change
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
    setCurrentPage(1);
  };

  const handleViewDetails = (player) => {
    setSelectedPlayer(player);
    setShowPlayerModal(true);
  };

  const handleCompareSelected = () => {
    if (selectedPlayers.length >= 2) {
      // Navigate to comparison page
      window.location.href = '/compare';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Players</h1>
          <p className="text-dark-400 mt-1">
            Browse and analyze FPL players with detailed statistics
          </p>
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center space-x-2">
          <Button
            variant={viewMode === 'cards' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setViewMode('cards')}
            icon={<Squares2X2Icon className="h-4 w-4" />}
          >
            Cards
          </Button>
          <Button
            variant={viewMode === 'table' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setViewMode('table')}
            icon={<TableCellsIcon className="h-4 w-4" />}
          >
            Table
          </Button>
        </div>
      </div>

      {/* Selected Players Bar */}
      {selectedPlayers.length > 0 && (
        <Card className="bg-primary-900 bg-opacity-20 border-primary-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Badge variant="primary" size="lg">
                  {selectedPlayers.length} Selected
                </Badge>
                <span className="text-white">
                  {selectedPlayers.map(p => p.web_name).join(', ')}
                </span>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              {selectedPlayers.length >= 2 && (
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleCompareSelected}
                  icon={<ArrowsRightLeftIcon className="h-4 w-4" />}
                >
                  Compare Players
                </Button>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={clearSelectedPlayers}
              >
                Clear Selection
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Filters */}
      <PlayerFilters
        onFiltersChange={handleFiltersChange}
        onSearch={handleSearch}
        isLoading={isLoading}
      />

      {/* Quick Stats */}
      {playersData && playersData.length > 0 && (
        <PlayerStats players={playersData} isLoading={isLoading} />
      )}

      {/* Results */}
      {error ? (
        <Card title="Error" className="border-danger-700">
          <div className="text-center py-8">
            <p className="text-danger-400 mb-4">
              Failed to load players: {error.message}
            </p>
            <Button variant="primary" onClick={refetch}>
              Try Again
            </Button>
          </div>
        </Card>
      ) : (
        <Card
          title={
            <div className="flex items-center justify-between w-full">
              <span>
                {searchQuery ? `Search Results for "${searchQuery}"` : 'All Players'}
              </span>
              {playersData && (
                <Badge variant="outline">
                  {Array.isArray(playersData) ? playersData.length : 0} players
                </Badge>
              )}
            </div>
          }
          padding={false}
        >
          {isLoading ? (
            <div className="p-8">
              <LoadingSpinner size="lg" text="Loading players..." />
            </div>
          ) : viewMode === 'cards' ? (
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {playersData?.map((player) => (
                  <PlayerCard
                    key={player.id}
                    player={player}
                    onViewDetails={() => handleViewDetails(player)}
                  />
                ))}
              </div>
            </div>
          ) : (
            <PlayerTable
              players={playersData}
              onViewDetails={handleViewDetails}
              isLoading={isLoading}
            />
          )}
        </Card>
      )}

      {/* Pagination */}
      {playersData && playersData.length === playersPerPage && (
        <div className="flex justify-center">
          <div className="flex space-x-2">
            <Button
              variant="secondary"
              disabled={currentPage === 1}
              onClick={() => setCurrentPage(currentPage - 1)}
            >
              Previous
            </Button>
            <Badge variant="outline" size="lg">
              Page {currentPage}
            </Badge>
            <Button
              variant="secondary"
              onClick={() => setCurrentPage(currentPage + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      )}

      {/* Player Detail Modal */}
      <PlayerDetailModal
        player={selectedPlayer}
        isOpen={showPlayerModal}
        onClose={() => {
          setShowPlayerModal(false);
          setSelectedPlayer(null);
        }}
      />
    </div>
  );
};

export default Players;
