import React from 'react';
import {
  TrophyIcon,
  ArrowRightIcon,
  SparklesIcon
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

  const renderSquadRecommendation = () => {
    // Group players by position
    const playersByPosition = {
      GK: recommendation.players?.filter(p => p.position === 'GK') || [],
      DEF: recommendation.players?.filter(p => p.position === 'DEF') || [],
      MID: recommendation.players?.filter(p => p.position === 'MID') || [],
      FWD: recommendation.players?.filter(p => p.position === 'FWD') || []
    };

    const totalCost = recommendation.budget_used || recommendation.total_cost || 0;
    const predictedPoints = recommendation.predicted_points || 0;

    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-dark-400">Formation: {recommendation.formation}</p>
            <p className="text-sm text-dark-400">Budget Used: £{totalCost}m</p>
            <p className="text-sm text-dark-400">Predicted Points: {predictedPoints}</p>
          </div>
          <Badge variant={getConfidenceColor(recommendation.analysis?.confidence_score || recommendation.confidence)}>
            {Math.round((recommendation.analysis?.confidence_score || recommendation.confidence || 0.85) * 100)}% confidence
          </Badge>
        </div>

        {/* Squad by Position */}
        <div className="space-y-3">
          {Object.entries(playersByPosition).map(([position, players]) => (
            players.length > 0 && (
              <div key={position}>
                <h4 className="text-sm font-medium text-white mb-2">
                  {position} ({players.length})
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                  {players.map((player, index) => (
                    <div key={index} className="bg-dark-800 rounded p-2">
                      <p className="text-sm font-medium text-white">{player.player_name}</p>
                      <p className="text-xs text-dark-400">{player.team} • £{player.price}m</p>
                      <p className="text-xs text-primary-400">{player.predicted_points} pts</p>
                      {player.reasoning && (
                        <p className="text-xs text-dark-500 mt-1 truncate" title={player.reasoning}>
                          {player.reasoning}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )
          ))}
        </div>

        {/* AI Analysis */}
        {recommendation.analysis && (
          <div className="bg-dark-800 rounded p-3">
            <h4 className="text-sm font-medium text-white mb-2">Analysis</h4>
            {recommendation.analysis.key_insights && (
              <div className="mb-2">
                <p className="text-xs text-dark-400 mb-1">Key Insights:</p>
                <ul className="text-xs text-dark-300">
                  {recommendation.analysis.key_insights.map((insight, i) => (
                    <li key={i}>• {insight}</li>
                  ))}
                </ul>
              </div>
            )}
            <p className="text-sm text-dark-300">
              {recommendation.ai_summary || recommendation.ai_reasoning}
            </p>
          </div>
        )}

        {/* Squad Stats */}
        <div className="grid grid-cols-3 gap-4 text-center">
          <div className="bg-dark-800 rounded p-2">
            <p className="text-xs text-dark-400">Players</p>
            <p className="text-sm font-medium text-white">{recommendation.players?.length || 0}/15</p>
          </div>
          <div className="bg-dark-800 rounded p-2">
            <p className="text-xs text-dark-400">Budget Left</p>
            <p className="text-sm font-medium text-white">£{(100 - totalCost).toFixed(1)}m</p>
          </div>
          <div className="bg-dark-800 rounded p-2">
            <p className="text-xs text-dark-400">Data Source</p>
            <p className="text-sm font-medium text-white">
              {recommendation.analysis?.players_analyzed || 'Real'} players
            </p>
          </div>
        </div>
      </div>
    );
  };

  const renderTransferRecommendation = () => {
    // Handle both old and new data structures
    const transfers = recommendation.transfers || recommendation.priority_transfers || [];
    const transfersCount = recommendation.transfers_suggested || transfers.length || 0;
    const totalGain = recommendation.analysis?.total_expected_gain ||
                     transfers.reduce((sum, t) => sum + (t.expected_gain || 0), 0);

    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <p className="text-sm text-dark-400">
            {transfersCount} transfer{transfersCount > 1 ? 's' : ''} suggested
          </p>
          <Badge variant="primary">
            +{totalGain?.toFixed(1)} pts
          </Badge>
        </div>

        {/* Squad Analysis (for new LLM responses) */}
        {recommendation.squad_analysis && (
          <div className="bg-dark-800 rounded p-3">
            <h4 className="text-sm font-medium text-white mb-2">Squad Analysis</h4>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <span className="text-success-400">Strengths:</span>
                <ul className="text-dark-300 mt-1">
                  {recommendation.squad_analysis.strengths?.map((strength, i) => (
                    <li key={i}>• {strength}</li>
                  ))}
                </ul>
              </div>
              <div>
                <span className="text-warning-400">Weaknesses:</span>
                <ul className="text-dark-300 mt-1">
                  {recommendation.squad_analysis.weaknesses?.map((weakness, i) => (
                    <li key={i}>• {weakness}</li>
                  ))}
                </ul>
              </div>
            </div>
            {recommendation.squad_analysis.overall_rating && (
              <div className="mt-2 text-center">
                <Badge variant="primary" size="sm">
                  Rating: {recommendation.squad_analysis.overall_rating}/10
                </Badge>
              </div>
            )}
          </div>
        )}

        {transfers.slice(0, 2).map((transfer, index) => (
          <div key={index} className="bg-dark-800 rounded p-3">
            <div className="flex items-center justify-between mb-2">
              <Badge variant="outline" size="sm">Priority {transfer.priority}</Badge>
              <Badge variant="success" size="sm">+{transfer.expected_gain} pts</Badge>
            </div>

            <div className="flex items-center space-x-3">
              <div className="text-center">
                <p className="text-sm font-medium text-white">{transfer.out.player_name}</p>
                <p className="text-xs text-dark-400">{transfer.out.team || 'Unknown'}</p>
                <p className="text-xs text-danger-400">OUT</p>
              </div>

              <ArrowRightIcon className="h-4 w-4 text-dark-500" />

              <div className="text-center">
                <p className="text-sm font-medium text-white">{transfer.in.player_name}</p>
                <p className="text-xs text-dark-400">{transfer.in.team || 'Unknown'}</p>
                <p className="text-xs text-success-400">IN</p>
              </div>
            </div>

            <div className="mt-2 space-y-1">
              <p className="text-xs text-dark-300">{transfer.out.reason}</p>
              <p className="text-xs text-dark-300">{transfer.in.reason}</p>
            </div>
          </div>
        ))}

        {/* Alternative Strategies (for new LLM responses) */}
        {recommendation.alternative_strategies && recommendation.alternative_strategies.length > 0 && (
          <div className="bg-dark-800 rounded p-3">
            <h4 className="text-sm font-medium text-white mb-2">Alternative Strategy</h4>
            {recommendation.alternative_strategies.slice(0, 1).map((strategy, index) => (
              <div key={index}>
                <p className="text-xs font-medium text-primary-400">{strategy.strategy}</p>
                <p className="text-xs text-dark-300 mt-1">{strategy.reasoning}</p>
              </div>
            ))}
          </div>
        )}

        <div className="bg-dark-800 rounded p-3">
          <p className="text-sm text-dark-300">{recommendation.ai_summary}</p>
        </div>
      </div>
    );
  };

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
