import React from 'react';
import { 
  PlusIcon, 
  EyeIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  MinusIcon
} from '@heroicons/react/24/outline';
import Badge from '../UI/Badge';
import Button from '../UI/Button';
import { useData } from '../../context/DataContext';

const PlayerCard = ({ player, onViewDetails, onCompare }) => {
  const { addSelectedPlayer, removeSelectedPlayer, selectedPlayers, formatPrice } = useData();
  
  const isSelected = selectedPlayers.some(p => p.id === player.id);
  
  const getPositionColor = (elementType) => {
    const colors = {
      1: 'bg-yellow-500', // GK
      2: 'bg-green-500',  // DEF
      3: 'bg-blue-500',   // MID
      4: 'bg-red-500'     // FWD
    };
    return colors[elementType] || 'bg-gray-500';
  };

  const getPositionName = (elementType) => {
    const positions = { 1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD' };
    return positions[elementType] || 'Unknown';
  };

  const getAvailabilityStatus = (status, chanceOfPlaying) => {
    if (status === 'i') return { text: 'Injured', color: 'danger' };
    if (status === 'u') return { text: 'Unavailable', color: 'danger' };
    if (status === 'd') return { text: 'Doubtful', color: 'warning' };
    if (chanceOfPlaying !== null && chanceOfPlaying < 75) {
      return { text: `${chanceOfPlaying}% chance`, color: 'warning' };
    }
    return { text: 'Available', color: 'success' };
  };

  const getFormTrend = (form) => {
    if (form >= 6) return { icon: ArrowTrendingUpIcon, color: 'text-success-500' };
    if (form <= 3) return { icon: ArrowTrendingDownIcon, color: 'text-danger-500' };
    return { icon: MinusIcon, color: 'text-dark-400' };
  };

  const availability = getAvailabilityStatus(player.status, player.chance_of_playing_this_round);
  const formTrend = getFormTrend(player.form);
  const FormIcon = formTrend.icon;

  const handleToggleSelection = () => {
    if (isSelected) {
      removeSelectedPlayer(player.id);
    } else {
      addSelectedPlayer(player);
    }
  };

  // Calculate value (points per million)
  const value = player.total_points / (player.now_cost / 10);

  return (
    <div className="bg-dark-900 border border-dark-700 rounded-xl p-4 hover:border-dark-600 transition-all duration-200 hover:shadow-lg">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-3">
          {/* Position Badge */}
          <div className={`w-8 h-8 ${getPositionColor(player.element_type)} rounded-full flex items-center justify-center`}>
            <span className="text-white text-xs font-bold">
              {getPositionName(player.element_type)}
            </span>
          </div>
          
          {/* Player Info */}
          <div>
            <h3 className="font-semibold text-white text-sm">{player.web_name}</h3>
            <p className="text-xs text-dark-400">{player.team?.name || 'Unknown Team'}</p>
          </div>
        </div>

        {/* Price */}
        <div className="text-right">
          <p className="text-lg font-bold text-white">£{formatPrice(player.now_cost)}</p>
          {player.cost_change_event !== 0 && (
            <p className={`text-xs ${player.cost_change_event > 0 ? 'text-success-500' : 'text-danger-500'}`}>
              {player.cost_change_event > 0 ? '+' : ''}£{(player.cost_change_event / 10).toFixed(1)}
            </p>
          )}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-3 gap-3 mb-3">
        <div className="text-center">
          <p className="text-xs text-dark-400">Points</p>
          <p className="text-lg font-bold text-white">{player.total_points}</p>
        </div>
        <div className="text-center">
          <p className="text-xs text-dark-400">PPG</p>
          <p className="text-lg font-bold text-white">{player.points_per_game}</p>
        </div>
        <div className="text-center">
          <p className="text-xs text-dark-400">Form</p>
          <div className="flex items-center justify-center space-x-1">
            <p className="text-lg font-bold text-white">{player.form}</p>
            <FormIcon className={`h-4 w-4 ${formTrend.color}`} />
          </div>
        </div>
      </div>

      {/* Performance Stats */}
      <div className="grid grid-cols-2 gap-2 mb-3 text-xs">
        <div className="flex justify-between">
          <span className="text-dark-400">Goals:</span>
          <span className="text-white">{player.goals_scored}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-dark-400">Assists:</span>
          <span className="text-white">{player.assists}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-dark-400">xG:</span>
          <span className="text-white">{player.expected_goals?.toFixed(1) || '0.0'}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-dark-400">xA:</span>
          <span className="text-white">{player.expected_assists?.toFixed(1) || '0.0'}</span>
        </div>
      </div>

      {/* Badges */}
      <div className="flex flex-wrap gap-1 mb-3">
        <Badge variant={availability.color} size="sm">
          {availability.text}
        </Badge>
        <Badge variant="outline" size="sm">
          {player.selected_by_percent}% owned
        </Badge>
        <Badge variant="outline" size="sm">
          Value: {value.toFixed(1)}
        </Badge>
      </div>

      {/* News */}
      {player.news && (
        <div className="mb-3 p-2 bg-dark-800 rounded text-xs text-dark-300">
          {player.news}
        </div>
      )}

      {/* Actions */}
      <div className="flex space-x-2">
        <Button
          variant="primary"
          size="sm"
          onClick={onViewDetails}
          icon={<EyeIcon className="h-4 w-4" />}
          className="flex-1"
        >
          Details
        </Button>
        
        <Button
          variant={isSelected ? "danger" : "secondary"}
          size="sm"
          onClick={handleToggleSelection}
          icon={isSelected ? <MinusIcon className="h-4 w-4" /> : <PlusIcon className="h-4 w-4" />}
        >
          {isSelected ? 'Remove' : 'Compare'}
        </Button>
      </div>
    </div>
  );
};

export default PlayerCard;
