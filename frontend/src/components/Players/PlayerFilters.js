import React, { useState } from 'react';
import { 
  MagnifyingGlassIcon, 
  FunnelIcon,
  XMarkIcon,
  AdjustmentsHorizontalIcon
} from '@heroicons/react/24/outline';
import Button from '../UI/Button';
import { useData } from '../../context/DataContext';

const PlayerFilters = ({ onFiltersChange, onSearch, isLoading = false }) => {
  const { filters, updateFilters, resetFilters } = useData();
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const positions = [
    { value: '', label: 'All Positions' },
    { value: 'GK', label: 'Goalkeepers' },
    { value: 'DEF', label: 'Defenders' },
    { value: 'MID', label: 'Midfielders' },
    { value: 'FWD', label: 'Forwards' }
  ];

  const teams = [
    { value: '', label: 'All Teams' },
    { value: 'Arsenal', label: 'Arsenal' },
    { value: 'Aston Villa', label: 'Aston Villa' },
    { value: 'Bournemouth', label: 'Bournemouth' },
    { value: 'Brentford', label: 'Brentford' },
    { value: 'Brighton', label: 'Brighton' },
    { value: 'Chelsea', label: 'Chelsea' },
    { value: 'Crystal Palace', label: 'Crystal Palace' },
    { value: 'Everton', label: 'Everton' },
    { value: 'Fulham', label: 'Fulham' },
    { value: 'Ipswich', label: 'Ipswich' },
    { value: 'Leicester', label: 'Leicester' },
    { value: 'Liverpool', label: 'Liverpool' },
    { value: 'Manchester City', label: 'Manchester City' },
    { value: 'Manchester Utd', label: 'Manchester Utd' },
    { value: 'Newcastle', label: 'Newcastle' },
    { value: 'Nottingham Forest', label: 'Nottingham Forest' },
    { value: 'Southampton', label: 'Southampton' },
    { value: 'Tottenham', label: 'Tottenham' },
    { value: 'West Ham', label: 'West Ham' },
    { value: 'Wolves', label: 'Wolves' }
  ];

  const sortOptions = [
    { value: 'total_points', label: 'Total Points' },
    { value: 'points_per_game', label: 'Points per Game' },
    { value: 'form', label: 'Form' },
    { value: 'now_cost', label: 'Price' },
    { value: 'selected_by_percent', label: 'Ownership %' },
    { value: 'goals_scored', label: 'Goals' },
    { value: 'assists', label: 'Assists' },
    { value: 'expected_goals', label: 'Expected Goals' },
    { value: 'expected_assists', label: 'Expected Assists' }
  ];

  const handleFilterChange = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    updateFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      onSearch(searchQuery.trim());
    }
  };

  const handleReset = () => {
    setSearchQuery('');
    resetFilters();
    onFiltersChange({});
    onSearch('');
  };

  const hasActiveFilters = Object.values(filters).some(value => value !== '' && value !== null);

  return (
    <div className="bg-dark-900 border border-dark-700 rounded-xl p-6 space-y-4">
      {/* Search Bar */}
      <form onSubmit={handleSearch} className="flex space-x-2">
        <div className="flex-1 relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-dark-400" />
          </div>
          <input
            type="text"
            placeholder="Search players by name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input pl-10 w-full"
          />
        </div>
        <Button 
          type="submit" 
          variant="primary"
          loading={isLoading}
          disabled={!searchQuery.trim()}
        >
          Search
        </Button>
      </form>

      {/* Quick Filters */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {/* Position Filter */}
        <div>
          <label className="block text-sm font-medium text-dark-300 mb-1">
            Position
          </label>
          <select
            value={filters.position}
            onChange={(e) => handleFilterChange('position', e.target.value)}
            className="select w-full"
          >
            {positions.map(pos => (
              <option key={pos.value} value={pos.value}>
                {pos.label}
              </option>
            ))}
          </select>
        </div>

        {/* Team Filter */}
        <div>
          <label className="block text-sm font-medium text-dark-300 mb-1">
            Team
          </label>
          <select
            value={filters.team}
            onChange={(e) => handleFilterChange('team', e.target.value)}
            className="select w-full"
          >
            {teams.map(team => (
              <option key={team.value} value={team.value}>
                {team.label}
              </option>
            ))}
          </select>
        </div>

        {/* Sort By */}
        <div>
          <label className="block text-sm font-medium text-dark-300 mb-1">
            Sort By
          </label>
          <select
            value={filters.sortBy}
            onChange={(e) => handleFilterChange('sortBy', e.target.value)}
            className="select w-full"
          >
            {sortOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Sort Order */}
        <div>
          <label className="block text-sm font-medium text-dark-300 mb-1">
            Order
          </label>
          <select
            value={filters.sortOrder}
            onChange={(e) => handleFilterChange('sortOrder', e.target.value)}
            className="select w-full"
          >
            <option value="desc">High to Low</option>
            <option value="asc">Low to High</option>
          </select>
        </div>

        {/* Actions */}
        <div className="flex items-end space-x-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setShowAdvanced(!showAdvanced)}
            icon={<AdjustmentsHorizontalIcon className="h-4 w-4" />}
          >
            Advanced
          </Button>
          {hasActiveFilters && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleReset}
              icon={<XMarkIcon className="h-4 w-4" />}
            >
              Reset
            </Button>
          )}
        </div>
      </div>

      {/* Advanced Filters */}
      {showAdvanced && (
        <div className="border-t border-dark-700 pt-4 space-y-4">
          <h4 className="text-sm font-medium text-white flex items-center">
            <FunnelIcon className="h-4 w-4 mr-2" />
            Advanced Filters
          </h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Price Range */}
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-1">
                Min Price (£m)
              </label>
              <input
                type="number"
                step="0.1"
                min="3.5"
                max="15.0"
                value={filters.minPrice}
                onChange={(e) => handleFilterChange('minPrice', e.target.value)}
                className="input w-full"
                placeholder="3.5"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-dark-300 mb-1">
                Max Price (£m)
              </label>
              <input
                type="number"
                step="0.1"
                min="3.5"
                max="15.0"
                value={filters.maxPrice}
                onChange={(e) => handleFilterChange('maxPrice', e.target.value)}
                className="input w-full"
                placeholder="15.0"
              />
            </div>

            {/* Availability */}
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-1">
                Availability
              </label>
              <select
                value={filters.availability || ''}
                onChange={(e) => handleFilterChange('availability', e.target.value)}
                className="select w-full"
              >
                <option value="">All Players</option>
                <option value="available">Available</option>
                <option value="doubtful">Doubtful</option>
                <option value="injured">Injured</option>
              </select>
            </div>

            {/* Form Filter */}
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-1">
                Min Form
              </label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="10"
                value={filters.minForm || ''}
                onChange={(e) => handleFilterChange('minForm', e.target.value)}
                className="input w-full"
                placeholder="0.0"
              />
            </div>
          </div>
        </div>
      )}

      {/* Active Filters Summary */}
      {hasActiveFilters && (
        <div className="flex flex-wrap gap-2 pt-2 border-t border-dark-700">
          <span className="text-sm text-dark-400">Active filters:</span>
          {filters.position && (
            <span className="badge bg-primary-500 text-white">
              Position: {positions.find(p => p.value === filters.position)?.label}
            </span>
          )}
          {filters.team && (
            <span className="badge bg-primary-500 text-white">
              Team: {filters.team}
            </span>
          )}
          {filters.minPrice && (
            <span className="badge bg-primary-500 text-white">
              Min Price: £{filters.minPrice}m
            </span>
          )}
          {filters.maxPrice && (
            <span className="badge bg-primary-500 text-white">
              Max Price: £{filters.maxPrice}m
            </span>
          )}
        </div>
      )}
    </div>
  );
};

export default PlayerFilters;
