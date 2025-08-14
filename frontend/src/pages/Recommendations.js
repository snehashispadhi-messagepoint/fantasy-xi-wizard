import React, { useState } from 'react';
import { useQuery } from 'react-query';
import {
  SparklesIcon,
  TrophyIcon,
  ArrowRightIcon,
  ChatBubbleLeftRightIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline';

import Card from '../components/UI/Card';
import Button from '../components/UI/Button';
import Badge from '../components/UI/Badge';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import AIChat from '../components/AI/AIChat';
import AIRecommendationCard from '../components/AI/AIRecommendationCard';

import { apiService } from '../services/apiService';

const Recommendations = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [showChat, setShowChat] = useState(false);
  const [fplUserId, setFplUserId] = useState('');
  const [fplTransferRec, setFplTransferRec] = useState(null);
  const [fplTransferLoading, setFplTransferLoading] = useState(false);
  const [manualSquad, setManualSquad] = useState('');
  const [manualSquadLoading, setManualSquadLoading] = useState(false);
  const [squadBudget, setSquadBudget] = useState(100.0);
  const [squadFormation, setSquadFormation] = useState('3-5-2');
  const [customSquadRec, setCustomSquadRec] = useState(null);
  const [customSquadLoading, setCustomSquadLoading] = useState(false);
  const [customCaptainRec, setCustomCaptainRec] = useState(null);
  const [customCaptainLoading, setCustomCaptainLoading] = useState(false);

  // Fetch different types of recommendations
  const { data: squadRec, isLoading: squadLoading } = useQuery(
    'squad-recommendation',
    () => apiService.getSquadRecommendation(),
    { staleTime: 10 * 60 * 1000 }
  );

  const { data: captainRec, isLoading: captainLoading } = useQuery(
    'captain-recommendation',
    () => apiService.getCaptainRecommendation(),
    { staleTime: 5 * 60 * 1000 }
  );

  const { data: transferRec, isLoading: transferLoading } = useQuery(
    'transfer-recommendation',
    () => apiService.getTransferRecommendation([]),
    { staleTime: 10 * 60 * 1000 }
  );

  const { data: chipRec, isLoading: chipLoading } = useQuery(
    'chip-recommendation',
    () => apiService.getChipRecommendation(['triple_captain', 'bench_boost', 'free_hit']),
    { staleTime: 30 * 60 * 1000 }
  );

  // Manual trigger functions for generating recommendations
  const handleGenerateSquad = async () => {
    setCustomSquadLoading(true);
    setCustomSquadRec(null);

    try {
      const response = await apiService.getSquadRecommendation(squadBudget, squadFormation, 3);
      setCustomSquadRec(response);
    } catch (error) {
      console.error('Error generating squad recommendation:', error);
      // You could add a toast notification here
    } finally {
      setCustomSquadLoading(false);
    }
  };

  const handleGenerateTransfer = () => {
    // Trigger transfer recommendation generation
    console.log('Generating transfer recommendation...');
  };

  const handleGenerateCaptain = async () => {
    setCustomCaptainLoading(true);
    setCustomCaptainRec(null);

    try {
      const response = await apiService.getCaptainRecommendation(null, 1);
      setCustomCaptainRec(response);
    } catch (error) {
      console.error('Error generating captain recommendation:', error);
      // You could add a toast notification here
    } finally {
      setCustomCaptainLoading(false);
    }
  };

  const handleGenerateChip = () => {
    // Trigger chip recommendation generation
    console.log('Generating chip recommendation...');
  };

  const handleAnalyzeFPLTeam = async () => {
    if (!fplUserId) return;

    setFplTransferLoading(true);
    setFplTransferRec(null);

    try {
      const response = await apiService.getFPLTransferRecommendation(parseInt(fplUserId), 3);
      setFplTransferRec(response);
    } catch (error) {
      console.error('Error fetching FPL transfer recommendations:', error);
      // You could add a toast notification here
    } finally {
      setFplTransferLoading(false);
    }
  };

  const handleAnalyzeManualSquad = async () => {
    if (!manualSquad.trim()) return;

    setManualSquadLoading(true);
    setFplTransferRec(null);

    try {
      // Parse manual squad input
      const playerNames = manualSquad.split('\n').filter(name => name.trim()).map(name => name.trim());

      const response = await apiService.analyzeManualSquad(playerNames, 3);
      setFplTransferRec(response);
    } catch (error) {
      console.error('Error analyzing manual squad:', error);
      // You could add a toast notification here
    } finally {
      setManualSquadLoading(false);
    }
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: SparklesIcon },
    { id: 'squad', label: 'Squad', icon: TrophyIcon },
    { id: 'transfers', label: 'Transfers', icon: ArrowRightIcon },
    { id: 'captain', label: 'Captain', icon: TrophyIcon },
    { id: 'chips', label: 'Chips', icon: CpuChipIcon }
  ];

  const renderOverview = () => (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Quick Recommendations */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold text-white">Quick Recommendations</h2>

        {captainLoading ? (
          <Card><LoadingSpinner size="sm" text="Loading captain recommendation..." /></Card>
        ) : captainRec && (
          <AIRecommendationCard
            recommendation={captainRec}
            type="captain"
            onViewDetails={() => setActiveTab('captain')}
          />
        )}

        {transferLoading ? (
          <Card><LoadingSpinner size="sm" text="Loading transfer suggestions..." /></Card>
        ) : transferRec && (
          <AIRecommendationCard
            recommendation={transferRec}
            type="transfer"
            onViewDetails={() => setActiveTab('transfers')}
          />
        )}
      </div>

      {/* AI Chat */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-white">AI Assistant</h2>
          <Button
            variant="primary"
            size="sm"
            onClick={() => setShowChat(!showChat)}
            icon={<ChatBubbleLeftRightIcon className="h-4 w-4" />}
          >
            {showChat ? 'Hide Chat' : 'Open Chat'}
          </Button>
        </div>

        {showChat ? (
          <div className="h-96">
            <AIChat className="h-full" />
          </div>
        ) : (
          <Card title="AI Assistant" subtitle="Ask me anything about FPL strategy">
            <div className="text-center py-8">
              <SparklesIcon className="h-12 w-12 text-primary-500 mx-auto mb-4" />
              <p className="text-dark-400 mb-4">
                Get personalized FPL advice powered by AI
              </p>
              <Button
                variant="primary"
                onClick={() => setShowChat(true)}
                icon={<ChatBubbleLeftRightIcon className="h-4 w-4" />}
              >
                Start Conversation
              </Button>
            </div>
          </Card>
        )}
      </div>
    </div>
  );

  const renderSquadTab = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-white">Squad Recommendations</h2>
        <Button
          variant="primary"
          size="sm"
          onClick={handleGenerateSquad}
          loading={customSquadLoading}
        >
          Generate New Squad
        </Button>
      </div>

      {/* Squad Configuration */}
      <Card title="Squad Configuration" subtitle="Customize your 15-player squad parameters">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-2">
              Budget (£m)
            </label>
            <input
              type="number"
              min="50"
              max="100"
              step="0.5"
              className="w-full px-3 py-2 bg-dark-800 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              value={squadBudget}
              onChange={(e) => setSquadBudget(parseFloat(e.target.value))}
            />
            <p className="text-xs text-dark-400 mt-1">
              Total budget for 15 players
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-2">
              Squad Structure
            </label>
            <div className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-dark-300">
              2 GK • 5 DEF • 5 MID • 3 FWD
            </div>
            <p className="text-xs text-dark-400 mt-1">
              Standard FPL squad composition
            </p>
          </div>
          <div className="flex items-end">
            <Button
              variant="primary"
              onClick={handleGenerateSquad}
              loading={customSquadLoading}
              className="w-full"
            >
              Generate Optimal Squad
            </Button>
          </div>
        </div>
      </Card>

      {(squadLoading || customSquadLoading) ? (
        <Card><LoadingSpinner size="lg" text="Analyzing optimal squad combinations..." /></Card>
      ) : (customSquadRec || squadRec) ? (
        <AIRecommendationCard
          recommendation={customSquadRec || squadRec}
          type="squad"
          onAccept={() => console.log('Apply squad recommendation')}
          onViewDetails={() => console.log('View squad details')}
        />
      ) : (
        <Card title="Squad Analysis" subtitle="Get AI-powered squad recommendations">
          <div className="text-center py-8">
            <TrophyIcon className="h-12 w-12 text-primary-500 mx-auto mb-4" />
            <p className="text-dark-400 mb-4">
              Generate an optimal squad based on current form, fixtures, and value
            </p>
            <Button
              variant="primary"
              onClick={handleGenerateSquad}
              loading={squadLoading}
            >
              Generate Squad Recommendation
            </Button>
          </div>
        </Card>
      )}
    </div>
  );

  const renderTransfersTab = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-white">Transfer Recommendations</h2>
      </div>

      {/* Manual Team Input */}
      <Card title="Analyze Your FPL Team" subtitle="Enter your current squad to get personalized transfer recommendations">
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">
                FPL User ID (Optional)
              </label>
              <input
                type="number"
                placeholder="e.g., 1678712"
                className="w-full px-3 py-2 bg-dark-800 border border-dark-600 rounded-lg text-white placeholder-dark-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                value={fplUserId}
                onChange={(e) => setFplUserId(e.target.value)}
              />
              <p className="text-xs text-dark-400 mt-1">
                Note: FPL API requires authentication for private team data
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">
                Current Squad (Manual Input)
              </label>
              <textarea
                placeholder="Enter your 15 players, one per line:&#10;Haaland&#10;Salah&#10;Palmer&#10;..."
                className="w-full px-3 py-2 bg-dark-800 border border-dark-600 rounded-lg text-white placeholder-dark-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                rows="4"
                value={manualSquad}
                onChange={(e) => setManualSquad(e.target.value)}
              />
              <p className="text-xs text-dark-400 mt-1">
                Enter player names (web names work best, e.g., "M.Salah")
              </p>
            </div>
          </div>

          <div className="flex space-x-3">
            <Button
              variant="primary"
              onClick={handleAnalyzeFPLTeam}
              loading={fplTransferLoading}
              disabled={!fplUserId && !manualSquad.trim()}
            >
              {fplUserId ? 'Try FPL API' : 'Analyze Manual Squad'}
            </Button>
            {manualSquad.trim() && (
              <Button
                variant="secondary"
                onClick={handleAnalyzeManualSquad}
                loading={manualSquadLoading}
              >
                Analyze Manual Squad
              </Button>
            )}
          </div>
        </div>
      </Card>

      {fplTransferLoading ? (
        <Card><LoadingSpinner size="lg" text="Fetching your FPL team and analyzing transfer opportunities..." /></Card>
      ) : fplTransferRec ? (
        <AIRecommendationCard
          recommendation={fplTransferRec}
          type="transfer"
          onAccept={() => console.log('Apply FPL transfer recommendation')}
          onViewDetails={() => console.log('View FPL transfer details')}
        />
      ) : transferLoading ? (
        <Card><LoadingSpinner size="lg" text="Analyzing transfer opportunities..." /></Card>
      ) : transferRec ? (
        <AIRecommendationCard
          recommendation={transferRec}
          type="transfer"
          onAccept={() => console.log('Apply transfer recommendation')}
          onViewDetails={() => console.log('View transfer details')}
        />
      ) : (
        <Card title="Alternative: Generic Transfer Analysis" subtitle="Smart transfer suggestions based on form and fixtures">
          <div className="text-center py-8">
            <ArrowRightIcon className="h-12 w-12 text-primary-500 mx-auto mb-4" />
            <p className="text-dark-400 mb-4">
              Get general transfer recommendations based on current player form and fixtures
            </p>
            <Button
              variant="secondary"
              onClick={handleGenerateTransfer}
              loading={transferLoading}
            >
              Analyze Transfer Options
            </Button>
          </div>
        </Card>
      )}
    </div>
  );

  const renderCaptainTab = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-white">Captain Recommendations</h2>
        <Button
          variant="primary"
          size="sm"
          onClick={handleGenerateCaptain}
          loading={customCaptainLoading}
        >
          Generate Fresh Analysis
        </Button>
      </div>

      {(captainLoading || customCaptainLoading) ? (
        <Card><LoadingSpinner size="lg" text="Analyzing captaincy options with current FPL news..." /></Card>
      ) : (customCaptainRec || captainRec) ? (
        <AIRecommendationCard
          recommendation={customCaptainRec || captainRec}
          type="captain"
          onAccept={() => console.log('Apply captain recommendation')}
          onViewDetails={() => console.log('View captain analysis')}
        />
      ) : (
        <Card title="Captain Analysis" subtitle="AI-powered captaincy recommendations with current FPL news">
          <div className="text-center py-8">
            <TrophyIcon className="h-12 w-12 text-primary-500 mx-auto mb-4" />
            <p className="text-dark-400 mb-4">
              Get intelligent captain picks based on fixtures, form, ownership, and current FPL news
            </p>
            <Button
              variant="primary"
              onClick={handleGenerateCaptain}
              loading={customCaptainLoading}
            >
              Get Captain Recommendation
            </Button>
          </div>
        </Card>
      )}
    </div>
  );

  const renderChipsTab = () => (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-white">Chip Strategy</h2>

      {chipLoading ? (
        <Card><LoadingSpinner size="lg" text="Analyzing chip strategy..." /></Card>
      ) : chipRec ? (
        <AIRecommendationCard
          recommendation={chipRec}
          type="chip"
          onAccept={() => console.log('Apply chip strategy')}
          onViewDetails={() => console.log('View chip details')}
        />
      ) : (
        <Card title="Chip Strategy" subtitle="Optimal timing for your remaining chips">
          <div className="text-center py-8">
            <CpuChipIcon className="h-12 w-12 text-primary-500 mx-auto mb-4" />
            <p className="text-dark-400 mb-4">
              Get strategic advice on when to use your Triple Captain, Bench Boost, and Free Hit
            </p>
            <Button
              variant="primary"
              onClick={handleGenerateChip}
              loading={chipLoading}
            >
              Analyze Chip Strategy
            </Button>
          </div>
        </Card>
      )}
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview': return renderOverview();
      case 'squad': return renderSquadTab();
      case 'transfers': return renderTransfersTab();
      case 'captain': return renderCaptainTab();
      case 'chips': return renderChipsTab();
      default: return renderOverview();
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">AI Recommendations</h1>
          <p className="text-dark-400 mt-1">
            Get intelligent squad suggestions and transfer advice powered by AI
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <SparklesIcon className="h-6 w-6 text-yellow-500" />
          <Badge variant="primary">AI Powered</Badge>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-dark-700">
        <nav className="flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-500'
                    : 'border-transparent text-dark-400 hover:text-dark-300 hover:border-dark-600'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Content */}
      {renderTabContent()}
    </div>
  );
};

export default Recommendations;
