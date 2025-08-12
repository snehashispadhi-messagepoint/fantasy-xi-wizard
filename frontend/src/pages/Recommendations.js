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
  const handleGenerateSquad = () => {
    // Trigger squad recommendation generation
    console.log('Generating squad recommendation...');
  };

  const handleGenerateTransfer = () => {
    // Trigger transfer recommendation generation
    console.log('Generating transfer recommendation...');
  };

  const handleGenerateCaptain = () => {
    // Trigger captain recommendation generation
    console.log('Generating captain recommendation...');
  };

  const handleGenerateChip = () => {
    // Trigger chip recommendation generation
    console.log('Generating chip recommendation...');
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
        <Button variant="primary" size="sm">
          Generate New Squad
        </Button>
      </div>

      {squadLoading ? (
        <Card><LoadingSpinner size="lg" text="Analyzing optimal squad combinations..." /></Card>
      ) : squadRec ? (
        <AIRecommendationCard
          recommendation={squadRec}
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
        <Button variant="primary" size="sm">
          Analyze My Team
        </Button>
      </div>

      {transferLoading ? (
        <Card><LoadingSpinner size="lg" text="Analyzing transfer opportunities..." /></Card>
      ) : transferRec ? (
        <AIRecommendationCard
          recommendation={transferRec}
          type="transfer"
          onAccept={() => console.log('Apply transfer recommendation')}
          onViewDetails={() => console.log('View transfer details')}
        />
      ) : (
        <Card title="Transfer Analysis" subtitle="Smart transfer suggestions based on form and fixtures">
          <div className="text-center py-8">
            <ArrowRightIcon className="h-12 w-12 text-primary-500 mx-auto mb-4" />
            <p className="text-dark-400 mb-4">
              Get personalized transfer recommendations based on your current squad
            </p>
            <Button
              variant="primary"
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
      <h2 className="text-xl font-bold text-white">Captain Recommendations</h2>

      {captainLoading ? (
        <Card><LoadingSpinner size="lg" text="Analyzing captaincy options..." /></Card>
      ) : captainRec ? (
        <AIRecommendationCard
          recommendation={captainRec}
          type="captain"
          onAccept={() => console.log('Apply captain recommendation')}
          onViewDetails={() => console.log('View captain analysis')}
        />
      ) : (
        <Card title="Captain Analysis" subtitle="AI-powered captaincy recommendations">
          <div className="text-center py-8">
            <TrophyIcon className="h-12 w-12 text-primary-500 mx-auto mb-4" />
            <p className="text-dark-400 mb-4">
              Get intelligent captain picks based on fixtures, form, and ownership
            </p>
            <Button
              variant="primary"
              onClick={handleGenerateCaptain}
              loading={captainLoading}
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
