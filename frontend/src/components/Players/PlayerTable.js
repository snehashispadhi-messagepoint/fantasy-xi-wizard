import React, { useState } from 'react';
import { 
  ChevronUpIcon, 
  ChevronDownIcon,
  EyeIcon,
  PlusIcon,
  MinusIcon
} from '@heroicons/react/24/outline';
import Badge from '../UI/Badge';
import Button from '../UI/Button';
import { useData } from '../../context/DataContext';

const PlayerTable = ({ players, onViewDetails, isLoading = false }) => {
  const { addSelectedPlayer, removeSelectedPlayer, selectedPlayers, formatPrice } = useData();
  const [sortField, setSortField] = useState('total_points');
  const [sortDirection, setSortDirection] = useState('desc');

  const getPositionName = (elementType) => {
    const positions = { 1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD' };
    return positions[elementType] || 'Unknown';
  };

  const getPositionColor = (elementType) => {
    const colors = {
      1: 'warning', // GK
      2: 'success', // DEF
      3: 'primary', // MID
      4: 'danger'   // FWD
    };
    return colors[elementType] || 'gray';
  };

  const getAvailabilityBadge = (status, chanceOfPlaying) => {
    if (status === 'i') return { text: 'Injured', variant: 'danger' };
    if (status === 'u') return { text: 'Unavailable', variant: 'danger' };
    if (status === 'd') return { text: 'Doubtful', variant: 'warning' };
    if (chanceOfPlaying !== null && chanceOfPlaying < 75) {
      return { text: `${chanceOfPlaying}%`, variant: 'warning' };
    }
    return { text: 'Available', variant: 'success' };
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const sortedPlayers = React.useMemo(() => {
    if (!players) return [];
    
    return [...players].sort((a, b) => {
      let aValue = a[sortField];
      let bValue = b[sortField];
      
      // Handle special cases
      if (sortField === 'web_name') {
        aValue = aValue?.toLowerCase() || '';
        bValue = bValue?.toLowerCase() || '';
      }
      
      if (typeof aValue === 'string') {
        return sortDirection === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }
      
      // Numeric comparison
      aValue = Number(aValue) || 0;
      bValue = Number(bValue) || 0;
      
      return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
    });
  }, [players, sortField, sortDirection]);

  const SortableHeader = ({ field, children, className = "" }) => (
    <th 
      className={`px-6 py-3 cursor-pointer hover:bg-dark-700 transition-colors ${className}`}
      onClick={() => handleSort(field)}
    >
      <div className="flex items-center space-x-1">
        <span>{children}</span>
        {sortField === field && (
          sortDirection === 'asc' 
            ? <ChevronUpIcon className="h-4 w-4" />
            : <ChevronDownIcon className="h-4 w-4" />
        )}
      </div>
    </th>
  );

  const isSelected = (playerId) => selectedPlayers.some(p => p.id === playerId);

  const handleToggleSelection = (player) => {
    if (isSelected(player.id)) {
      removeSelectedPlayer(player.id);
    } else {
      addSelectedPlayer(player);
    }
  };

  if (isLoading) {
    return (
      <div className="bg-dark-900 border border-dark-700 rounded-xl p-8">
        <div className="animate-pulse space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-12 bg-dark-800 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (!players || players.length === 0) {
    return (
      <div className="bg-dark-900 border border-dark-700 rounded-xl p-8 text-center">
        <p className="text-dark-400">No players found matching your criteria.</p>
      </div>
    );
  }

  return (
    <div className="bg-dark-900 border border-dark-700 rounded-xl overflow-hidden">
      <div className="overflow-x-auto">
        <table className="table">
          <thead>
            <tr>
              <SortableHeader field="web_name">Player</SortableHeader>
              <SortableHeader field="element_type">Pos</SortableHeader>
              <SortableHeader field="team">Team</SortableHeader>
              <SortableHeader field="now_cost">Price</SortableHeader>
              <SortableHeader field="total_points">Points</SortableHeader>
              <SortableHeader field="points_per_game">PPG</SortableHeader>
              <SortableHeader field="form">Form</SortableHeader>
              <SortableHeader field="goals_scored">Goals</SortableHeader>
              <SortableHeader field="assists">Assists</SortableHeader>
              <SortableHeader field="expected_goals">xG</SortableHeader>
              <SortableHeader field="expected_assists">xA</SortableHeader>
              <SortableHeader field="selected_by_percent">Own%</SortableHeader>
              <th className="px-6 py-3">Status</th>
              <th className="px-6 py-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {sortedPlayers.map((player) => {
              const availability = getAvailabilityBadge(player.status, player.chance_of_playing_this_round);
              const value = player.total_points / (player.now_cost / 10);
              
              return (
                <tr key={player.id} className={isSelected(player.id) ? 'bg-primary-900 bg-opacity-20' : ''}>
                  <td className="px-6 py-4">
                    <div>
                      <div className="font-medium text-white">{player.web_name}</div>
                      <div className="text-sm text-dark-400">
                        {player.first_name} {player.second_name}
                      </div>
                    </div>
                  </td>
                  
                  <td className="px-6 py-4">
                    <Badge variant={getPositionColor(player.element_type)} size="sm">
                      {getPositionName(player.element_type)}
                    </Badge>
                  </td>
                  
                  <td className="px-6 py-4">
                    <span className="text-white">{player.team?.short_name || 'Unknown'}</span>
                  </td>
                  
                  <td className="px-6 py-4">
                    <div>
                      <span className="text-white font-medium">£{formatPrice(player.now_cost)}</span>
                      {player.cost_change_event !== 0 && (
                        <div className={`text-xs ${player.cost_change_event > 0 ? 'text-success-500' : 'text-danger-500'}`}>
                          {player.cost_change_event > 0 ? '+' : ''}£{(player.cost_change_event / 10).toFixed(1)}
                        </div>
                      )}
                    </div>
                  </td>
                  
                  <td className="px-6 py-4">
                    <span className="text-white font-medium">{player.total_points}</span>
                  </td>
                  
                  <td className="px-6 py-4">
                    <span className="text-white">{player.points_per_game}</span>
                  </td>
                  
                  <td className="px-6 py-4">
                    <span className="text-white">{player.form}</span>
                  </td>
                  
                  <td className="px-6 py-4">
                    <span className="text-white">{player.goals_scored}</span>
                  </td>
                  
                  <td className="px-6 py-4">
                    <span className="text-white">{player.assists}</span>
                  </td>
                  
                  <td className="px-6 py-4">
                    <span className="text-white">{player.expected_goals?.toFixed(1) || '0.0'}</span>
                  </td>
                  
                  <td className="px-6 py-4">
                    <span className="text-white">{player.expected_assists?.toFixed(1) || '0.0'}</span>
                  </td>
                  
                  <td className="px-6 py-4">
                    <span className="text-white">{player.selected_by_percent}%</span>
                  </td>
                  
                  <td className="px-6 py-4">
                    <Badge variant={availability.variant} size="sm">
                      {availability.text}
                    </Badge>
                  </td>
                  
                  <td className="px-6 py-4">
                    <div className="flex space-x-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onViewDetails(player)}
                        icon={<EyeIcon className="h-4 w-4" />}
                      />
                      <Button
                        variant={isSelected(player.id) ? "danger" : "ghost"}
                        size="sm"
                        onClick={() => handleToggleSelection(player)}
                        icon={isSelected(player.id) ? <MinusIcon className="h-4 w-4" /> : <PlusIcon className="h-4 w-4" />}
                      />
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      
      {/* Table Footer */}
      <div className="px-6 py-3 bg-dark-800 border-t border-dark-700">
        <div className="flex items-center justify-between text-sm text-dark-400">
          <span>Showing {sortedPlayers.length} players</span>
          <span>Value = Points per £1m</span>
        </div>
      </div>
    </div>
  );
};

export default PlayerTable;
