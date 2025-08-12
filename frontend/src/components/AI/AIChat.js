import React, { useState, useRef, useEffect } from 'react';
import { 
  PaperAirplaneIcon,
  SparklesIcon,
  UserIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline';
import { useQuery, useMutation } from 'react-query';

import Button from '../UI/Button';
import LoadingSpinner from '../UI/LoadingSpinner';
import { apiService } from '../../services/apiService';

const AIChat = ({ className = '' }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'ai',
      content: "Hello! I'm your FPL AI assistant (v2.0). Ask me anything about player recommendations, transfers, captaincy, or general FPL strategy!",
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // AI query mutation with enhanced error handling
  const aiQueryMutation = useMutation(
    (queryData) => {
      console.log('🔍 Mutation called with:', queryData);
      // Validate the data before sending
      if (!queryData || !queryData.query || !queryData.query.trim()) {
        throw new Error('Invalid query data');
      }
      return apiService.queryAI(queryData.query, queryData.context);
    },
    {
      retry: false, // Disable retry to prevent multiple invalid requests
      onSuccess: (response) => {
        console.log('AI Chat Success:', response);
        const aiMessage = {
          id: Date.now(),
          type: 'ai',
          content: response.response || response.ai_summary || 'I understand your question, but I need more context to provide a helpful answer.',
          data: response,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, aiMessage]);
      },
      onError: (error) => {
        console.error('AI Chat Error:', error);

        let errorContent = "I'm sorry, I'm having trouble processing your request. Please try again.";

        // Handle specific error types
        if (error.message.includes('Query cannot be empty')) {
          errorContent = "Please enter a question or message before sending.";
        } else if (error.message.includes('Server error')) {
          errorContent = "The AI service is temporarily unavailable. Please try again in a moment.";
        } else if (error.message.includes('Network error')) {
          errorContent = "Network connection issue. Please check your connection and try again.";
        }

        const errorMessage = {
          id: Date.now(),
          type: 'ai',
          content: errorContent,
          error: true,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    }
  );

  const handleSubmit = (e) => {
    e.preventDefault();

    // Validate input
    const trimmedInput = inputValue.trim();
    if (!trimmedInput || trimmedInput.length === 0 || aiQueryMutation.isLoading) {
      console.log('🚫 Empty query prevented:', { inputValue, trimmedInput });
      return;
    }

    console.log('📤 Sending AI query:', trimmedInput);

    // Add user message
    const userMessage = {
      id: Date.now() - 1,
      type: 'user',
      content: trimmedInput,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    // Send to AI with validation
    const queryData = {
      query: trimmedInput,
      context: {
        timestamp: new Date().toISOString(),
        messageCount: messages.length,
        gameweek: 1
      }
    };

    console.log('📤 Sending query data:', queryData);
    aiQueryMutation.mutate(queryData);

    setInputValue('');
  };

  const quickQuestions = [
    "Who should I captain this week?",
    "Best transfers for this gameweek?",
    "When should I use my Triple Captain?",
    "Best value players under £6m?",
    "Which defenders are worth buying?"
  ];

  const handleQuickQuestion = (question) => {
    if (question && question.trim()) {
      setInputValue(question.trim());
    }
  };

  const formatAIResponse = (message) => {
    // Handle team selection responses
    if (message.data?.query_type === 'team_selection' && message.data?.supporting_data?.team_selection) {
      const teamData = message.data.supporting_data.team_selection;
      const totalCost = message.data.supporting_data.total_cost;
      const remainingBudget = message.data.supporting_data.remaining_budget;
      const formation = message.data.supporting_data.formation;
      const captain = message.data.supporting_data.captain_recommendation;

      return (
        <div className="space-y-4">
          {/* Formation and Budget Header */}
          <div className="bg-primary-900 border border-primary-700 rounded-lg p-3">
            <div className="flex justify-between items-center">
              <h4 className="text-primary-200 font-semibold">Team Selection ({formation})</h4>
              <div className="text-right">
                <p className="text-primary-200 text-sm">Total: £{totalCost?.toFixed(1)}m</p>
                <p className="text-primary-300 text-xs">Remaining: £{remainingBudget?.toFixed(1)}m</p>
              </div>
            </div>
          </div>

          {/* Team Positions */}
          {Object.entries(teamData).map(([position, players]) => (
            <div key={position} className="bg-gray-100 dark:bg-dark-800 border border-gray-200 dark:border-dark-600 rounded-lg p-3">
              <h5 className="text-gray-900 dark:text-white font-medium mb-2 uppercase text-sm">
                {position === 'gk' ? 'Goalkeeper' :
                 position === 'def' ? 'Defenders' :
                 position === 'mid' ? 'Midfielders' : 'Forwards'}
              </h5>
              <div className="space-y-2">
                {players.map((player, index) => (
                  <div key={index} className="flex justify-between items-center bg-gray-50 dark:bg-dark-700 rounded p-2">
                    <div>
                      <p className="text-gray-900 dark:text-white font-medium text-sm">{player.name}</p>
                      <p className="text-gray-600 dark:text-dark-400 text-xs">
                        {player.team} • 2024-25: {player.last_season_points} pts ({player.goals}G {player.assists}A)
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-gray-900 dark:text-white font-semibold text-sm">£{player.price?.toFixed(1)}m</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {/* Captain Recommendation */}
          {captain && (
            <div className="bg-warning-900 border border-warning-700 rounded-lg p-3">
              <h5 className="text-warning-200 font-medium mb-1">👑 Captain Recommendation</h5>
              <p className="text-warning-100 text-sm">
                <span className="font-semibold">{captain.name}</span> ({captain.team}) - {captain.last_season_points} points in 2024-25
              </p>
            </div>
          )}

          {/* Key Recommendations */}
          {message.data?.key_recommendations && (
            <div className="bg-gray-100 dark:bg-dark-800 border border-gray-200 dark:border-dark-600 rounded-lg p-3">
              <h5 className="text-gray-900 dark:text-white font-medium mb-2">🎯 Key Insights</h5>
              <ul className="space-y-1">
                {message.data.key_recommendations.map((rec, index) => (
                  <li key={index} className="text-gray-700 dark:text-dark-300 text-sm">• {rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      );
    }

    // Handle captain recommendations
    if (message.data?.query_type === 'captain_recommendation' && message.data?.supporting_data?.captain_options) {
      const captainOptions = message.data.supporting_data.captain_options;

      return (
        <div className="space-y-3">
          <p className="text-gray-900 dark:text-white">{message.content}</p>

          <div className="bg-gray-100 dark:bg-dark-800 border border-gray-200 dark:border-dark-600 rounded-lg p-3">
            <h5 className="text-gray-900 dark:text-white font-medium mb-2">👑 Captain Options</h5>
            <div className="space-y-2">
              {captainOptions.map((option, index) => (
                <div key={index} className="flex justify-between items-center bg-gray-50 dark:bg-dark-700 rounded p-2">
                  <div>
                    <p className="text-gray-900 dark:text-white font-medium text-sm">{option.name}</p>
                    <p className="text-gray-600 dark:text-dark-400 text-xs">
                      {option.team} • {option.position} • 2024-25: {option.last_season_points} pts
                    </p>
                  </div>
                  <p className="text-gray-900 dark:text-white font-semibold text-sm">£{option.price?.toFixed(1)}m</p>
                </div>
              ))}
            </div>
          </div>

          {message.data?.key_recommendations && (
            <div className="bg-gray-100 dark:bg-dark-800 border border-gray-200 dark:border-dark-600 rounded-lg p-3">
              <h5 className="text-gray-900 dark:text-white font-medium mb-2">🎯 Analysis</h5>
              <ul className="space-y-1">
                {message.data.key_recommendations.map((rec, index) => (
                  <li key={index} className="text-gray-700 dark:text-dark-300 text-sm">• {rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      );
    }

    // Handle transfer recommendations
    if (message.data?.query_type === 'transfer_recommendation' && message.data?.supporting_data?.transfer_targets) {
      const transferTargets = message.data.supporting_data.transfer_targets;

      return (
        <div className="space-y-3">
          <p className="text-gray-900 dark:text-white">{message.content}</p>

          <div className="bg-gray-100 dark:bg-dark-800 border border-gray-200 dark:border-dark-600 rounded-lg p-3">
            <h5 className="text-gray-900 dark:text-white font-medium mb-2">🔄 Transfer Targets</h5>
            <div className="space-y-2">
              {transferTargets.map((target, index) => (
                <div key={index} className="flex justify-between items-center bg-gray-50 dark:bg-dark-700 rounded p-2">
                  <div>
                    <p className="text-gray-900 dark:text-white font-medium text-sm">{target.name}</p>
                    <p className="text-gray-600 dark:text-dark-400 text-xs">
                      {target.team} • {target.position} • 2024-25: {target.last_season_points} pts
                    </p>
                    {target.value_score && (
                      <p className="text-success-400 text-xs">Value: {target.value_score.toFixed(1)} pts/£m</p>
                    )}
                  </div>
                  <p className="text-gray-900 dark:text-white font-semibold text-sm">£{target.price?.toFixed(1)}m</p>
                </div>
              ))}
            </div>
          </div>

          {message.data?.key_recommendations && (
            <div className="bg-gray-100 dark:bg-dark-800 border border-gray-200 dark:border-dark-600 rounded-lg p-3">
              <h5 className="text-gray-900 dark:text-white font-medium mb-2">💡 Recommendations</h5>
              <ul className="space-y-1">
                {message.data.key_recommendations.map((rec, index) => (
                  <li key={index} className="text-gray-700 dark:text-dark-300 text-sm">• {rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      );
    }

    // Handle general recommendations with key picks
    if (message.data?.key_picks) {
      return (
        <div className="space-y-3">
          <p className="text-gray-900 dark:text-white">{message.content}</p>
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-primary-400">Key Recommendations:</h4>
            {message.data.key_picks.map((pick, index) => (
              <div key={index} className="bg-gray-100 dark:bg-dark-700 rounded p-2">
                <p className="font-medium text-gray-900 dark:text-white text-sm">{pick.name}</p>
                <p className="text-xs text-gray-600 dark:text-dark-300">{pick.reasoning}</p>
              </div>
            ))}
          </div>
        </div>
      );
    }

    // Default: just show the content with any key recommendations
    return (
      <div className="space-y-3">
        <div className="text-gray-900 dark:text-white whitespace-pre-wrap">{message.content}</div>

        {message.data?.key_recommendations && (
          <div className="bg-gray-100 dark:bg-dark-800 border border-gray-200 dark:border-dark-600 rounded-lg p-3">
            <h5 className="text-gray-900 dark:text-white font-medium mb-2">🎯 Key Points</h5>
            <ul className="space-y-1">
              {message.data.key_recommendations.map((rec, index) => (
                <li key={index} className="text-gray-700 dark:text-dark-300 text-sm">• {rec}</li>
              ))}
            </ul>
          </div>
        )}

        {message.data?.ai_mode && (
          <div className="text-xs text-gray-500 dark:text-dark-500 mt-2">
            Analysis mode: {message.data.ai_mode} • Confidence: {(message.data.confidence * 100).toFixed(0)}%
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={`flex flex-col h-full bg-white dark:bg-dark-900 border border-gray-200 dark:border-dark-700 rounded-xl ${className}`}>
      {/* Header */}
      <div className="flex items-center space-x-3 p-4 border-b border-gray-200 dark:border-dark-700">
        <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
          <SparklesIcon className="h-5 w-5 text-white" />
        </div>
        <div>
          <h3 className="font-semibold text-gray-900 dark:text-white">FPL AI Assistant</h3>
          <p className="text-xs text-gray-600 dark:text-dark-400">Powered by historical data & AI</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`flex space-x-2 max-w-[80%] ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
              {/* Avatar */}
              <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                message.type === 'user' 
                  ? 'bg-primary-600' 
                  : message.error 
                    ? 'bg-danger-600' 
                    : 'bg-success-600'
              }`}>
                {message.type === 'user' ? (
                  <UserIcon className="h-4 w-4 text-white" />
                ) : (
                  <CpuChipIcon className="h-4 w-4 text-white" />
                )}
              </div>

              {/* Message */}
              <div className={`rounded-lg p-3 ${
                message.type === 'user'
                  ? 'bg-primary-600 text-white'
                  : message.error
                    ? 'bg-danger-900 border border-danger-700 text-danger-200'
                    : 'bg-gray-50 dark:bg-dark-800 border border-gray-200 dark:border-dark-600 text-gray-900 dark:text-dark-100'
              }`}>
                {message.type === 'ai' ? formatAIResponse(message) : <p>{message.content}</p>}
                <p className="text-xs opacity-70 mt-2">
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          </div>
        ))}

        {/* Loading indicator */}
        {aiQueryMutation.isLoading && (
          <div className="flex justify-start">
            <div className="flex space-x-2 max-w-[80%]">
              <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
                <CpuChipIcon className="h-4 w-4 text-white" />
              </div>
              <div className="bg-gray-50 dark:bg-dark-800 border border-gray-200 dark:border-dark-600 rounded-lg p-3">
                <LoadingSpinner size="sm" text="Thinking..." />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Questions */}
      {messages.length <= 1 && (
        <div className="p-4 border-t border-gray-200 dark:border-dark-700">
          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">Quick Questions:</h4>
          <div className="flex flex-wrap gap-2">
            {quickQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => handleQuickQuestion(question)}
                className="text-xs px-3 py-1 bg-gray-200 dark:bg-dark-700 hover:bg-gray-300 dark:hover:bg-dark-600 text-gray-700 dark:text-dark-300 hover:text-gray-900 dark:hover:text-white rounded-full transition-colors"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200 dark:border-dark-700">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask me anything about FPL..."
            className="input flex-1"
            disabled={aiQueryMutation.isLoading}
          />
          <Button
            type="submit"
            variant="primary"
            disabled={!inputValue.trim() || aiQueryMutation.isLoading}
            loading={aiQueryMutation.isLoading}
            icon={<PaperAirplaneIcon className="h-4 w-4" />}
          >
            Send
          </Button>
        </div>
      </form>
    </div>
  );
};

export default AIChat;
