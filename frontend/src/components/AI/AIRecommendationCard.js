import React from 'react';
import { 
  TrophyIcon,
  ArrowRightIcon,
  SparklesIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

import Card from '../UI/Card';
import Button from '../UI/Button';
import Badge from '../UI/Badge';

const AIRecommendationCard = ({ 
  recommendation, 
  type, 
  onAccept, 
  onViewDetails,
  className = '' 
}) => {
  const getTypeIcon = () => {
    switch (type) {
      case 'squad': return <TrophyIcon className="h-5 w-5" />;
      case 'transfer': return <ArrowRightIcon className="h-5 w-5" />;
      case 'captain': return <TrophyIcon className="h-5 w-5" />;
      case 'chip': return <SparklesIcon className="h-5 w-5" />;
      default: return <SparklesIcon className="h-5 w-5" />;
    }
  };

  const getTypeTitle = () => {
    switch (type) {
      case 'squad': return 'Squad Recommendation';
      case 'transfer': return 'Transfer Suggestion';
      case 'captain': return 'Captain Pick';
      case 'chip': return 'Chip Strategy';
      default: return 'AI Recommendation';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'danger';
  };

  const renderSquadRecommendation = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-dark-400">Formation: {recommendation.formation}</p>
          <p className="text-sm text-dark-400">Budget Used: £{recommendation.budget_used}m</p>
        </div>
        <Badge variant={getConfidenceColor(recommendation.analysis?.confidence_score)}>
          {Math.round(recommendation.analysis?.confidence_score * 100)}% confidence
        </Badge>
      </div>

      <div>
        <h4 className="text-sm font-medium text-white mb-2">Key Players:</h4>
        <div className="grid grid-cols-2 gap-2">
          {recommendation.players?.slice(0, 4).map((player, index) => (
            <div key={index} className="bg-dark-800 rounded p-2">
              <p className="text-sm font-medium text-white">{player.player_name}</p>
              <p className="text-xs text-dark-400">{player.team} • £{player.price}m</p>
              <p className="text-xs text-primary-400">{player.predicted_points} pts</p>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-dark-800 rounded p-3">
        <p className="text-sm text-dark-300">{recommendation.ai_summary}</p>
      </div>

      {recommendation.analysis?.expected_total_points && (
        <div className="flex items-center justify-between text-sm">
          <span className="text-dark-400">Expected Points:</span>
          <span className="text-white font-medium">{recommendation.analysis.expected_total_points}</span>
        </div>
      )}
    </div>
  );

  const renderTransferRecommendation = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-dark-400">
          {recommendation.transfers_suggested} transfer{recommendation.transfers_suggested > 1 ? 's' : ''} suggested
        </p>
        <Badge variant="primary">
          +{recommendation.analysis?.total_expected_gain?.toFixed(1)} pts
        </Badge>
      </div>

      {recommendation.transfers?.slice(0, 2).map((transfer, index) => (
        <div key={index} className="bg-dark-800 rounded p-3">
          <div className="flex items-center justify-between mb-2">
            <Badge variant="outline" size="sm">Priority {transfer.priority}</Badge>
            <Badge variant="success" size="sm">+{transfer.expected_gain} pts</Badge>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="text-center">
              <p className="text-sm font-medium text-white">{transfer.out.player_name}</p>
              <p className="text-xs text-dark-400">{transfer.out.team}</p>
              <p className="text-xs text-danger-400">OUT</p>
            </div>
            
            <ArrowRightIcon className="h-4 w-4 text-dark-500" />
            
            <div className="text-center">
              <p className="text-sm font-medium text-white">{transfer.in.player_name}</p>
              <p className="text-xs text-dark-400">{transfer.in.team}</p>
              <p className="text-xs text-success-400">IN</p>
            </div>
          </div>
          
          <p className="text-xs text-dark-300 mt-2">{transfer.reasoning}</p>
        </div>
      ))}

      <div className="bg-dark-800 rounded p-3">
        <p className="text-sm text-dark-300">{recommendation.ai_summary}</p>
      </div>
    </div>
  );

  const renderCaptainRecommendation = () => (
    <div className="space-y-4">
      <div className="text-center">
        <p className="text-sm text-dark-400 mb-2">Gameweek {recommendation.gameweek}</p>
      </div>

      {recommendation.recommendations?.slice(0, 3).map((captain, index) => (
        <div key={index} className={`bg-dark-800 rounded p-3 ${index === 0 ? 'border border-primary-600' : ''}`}>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <h4 className="font-medium text-white">{captain.player_name}</h4>
              {index === 0 && <TrophyIcon className="h-4 w-4 text-yellow-500" />}
            </div>
            <Badge variant={getConfidenceColor(captain.confidence)}>
              {Math.round(captain.confidence * 100)}%
            </Badge>
          </div>
          
          <div className="grid grid-cols-2 gap-2 text-xs mb-2">
            <div>
              <span className="text-dark-400">Predicted:</span>
              <span className="text-white ml-1">{captain.predicted_points} pts</span>
            </div>
            <div>
              <span className="text-dark-400">Fixture:</span>
              <span className="text-white ml-1">{captain.fixture}</span>
            </div>
          </div>
          
          <p className="text-xs text-dark-300">{captain.reasoning}</p>
        </div>
      ))}

      <div className="bg-dark-800 rounded p-3">
        <p className="text-sm text-dark-300">{recommendation.ai_summary}</p>
      </div>
    </div>
  );

  const renderChipRecommendation = () => (
    <div className="space-y-4">
      {recommendation.recommendations?.slice(0, 2).map((chip, index) => (
        <div key={index} className="bg-dark-800 rounded p-3">
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-medium text-white">{chip.chip}</h4>
            <div className="flex items-center space-x-2">
              <Badge variant="primary" size="sm">GW{chip.recommended_gameweek}</Badge>
              <Badge variant={getConfidenceColor(chip.confidence)} size="sm">
                {Math.round(chip.confidence * 100)}%
              </Badge>
            </div>
          </div>
          
          <p className="text-sm text-dark-300 mb-2">{chip.reasoning}</p>
          
          <div className="flex items-center justify-between text-xs">
            <span className="text-dark-400">Expected Gain:</span>
            <span className="text-success-400 font-medium">+{chip.expected_gain} pts</span>
          </div>
        </div>
      ))}

      <div className="bg-dark-800 rounded p-3">
        <p className="text-sm text-dark-300">{recommendation.ai_summary}</p>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (type) {
      case 'squad': return renderSquadRecommendation();
      case 'transfer': return renderTransferRecommendation();
      case 'captain': return renderCaptainRecommendation();
      case 'chip': return renderChipRecommendation();
      default: return <p className="text-dark-400">Unknown recommendation type</p>;
    }
  };

  return (
    <Card 
      title={
        <div className="flex items-center space-x-2">
          <div className="text-primary-500">{getTypeIcon()}</div>
          <span>{getTypeTitle()}</span>
          <SparklesIcon className="h-4 w-4 text-yellow-500" />
        </div>
      }
      className={className}
    >
      {renderContent()}
      
      {/* Actions */}
      <div className="flex space-x-2 mt-4 pt-4 border-t border-dark-700">
        {onViewDetails && (
          <Button variant="secondary" size="sm" onClick={onViewDetails} className="flex-1">
            View Details
          </Button>
        )}
        {onAccept && (
          <Button variant="primary" size="sm" onClick={onAccept} className="flex-1">
            Apply Recommendation
          </Button>
        )}
      </div>
    </Card>
  );
};

export default AIRecommendationCard;
