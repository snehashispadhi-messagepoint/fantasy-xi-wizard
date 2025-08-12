import React, { useState } from 'react';
import { useQuery, useQueryClient } from 'react-query';
import { 
  ArrowPathIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

import Card from '../UI/Card';
import Button from '../UI/Button';
import Badge from '../UI/Badge';
import LoadingSpinner from '../UI/LoadingSpinner';

import { apiService } from '../../services/apiService';

const DataSync = ({ showStats = true, compact = false }) => {
  const [isSyncing, setIsSyncing] = useState(false);
  const [lastSyncResult, setLastSyncResult] = useState(null);
  const queryClient = useQueryClient();

  // Fetch database stats
  const { 
    data: dbStats, 
    isLoading: statsLoading,
    refetch: refetchStats 
  } = useQuery(
    'database-stats',
    () => apiService.getDatabaseStats(),
    {
      staleTime: 30 * 1000, // 30 seconds
      refetchInterval: 60 * 1000, // 1 minute
    }
  );

  const handleSyncData = async (force = false) => {
    setIsSyncing(true);
    setLastSyncResult(null);

    try {
      const response = await apiService.syncData(force);
      console.log('🔍 Sync response:', response);
      setLastSyncResult({
        success: true,
        message: response.message || 'Data sync completed successfully',
        timestamp: new Date()
      });

      // Invalidate all queries to refresh data
      queryClient.invalidateQueries();
      
      // Refetch stats after a short delay
      setTimeout(() => {
        refetchStats();
      }, 2000);

    } catch (error) {
      setLastSyncResult({
        success: false,
        message: error.response?.data?.detail || 'Failed to sync data',
        timestamp: new Date()
      });
    } finally {
      setIsSyncing(false);
    }
  };

  const getLastUpdateTime = () => {
    if (!dbStats) return 'Unknown';

    // This would ideally come from the API
    // For now, we'll show a relative time
    return 'Recently updated';
  };

  const getSyncStatusBadge = () => {
    if (isSyncing) {
      return <Badge variant="warning" size="sm">Syncing...</Badge>;
    }
    
    if (lastSyncResult) {
      return (
        <Badge 
          variant={lastSyncResult.success ? "success" : "danger"} 
          size="sm"
        >
          {lastSyncResult.success ? "Sync Complete" : "Sync Failed"}
        </Badge>
      );
    }
    
    return <Badge variant="outline" size="sm">Ready</Badge>;
  };

  if (compact) {
    return (
      <div className="flex items-center space-x-3">
        <Button
          variant="secondary"
          size="sm"
          onClick={() => handleSyncData(false)}
          disabled={isSyncing}
          icon={isSyncing ? <ClockIcon className="h-4 w-4 animate-spin" /> : <ArrowPathIcon className="h-4 w-4" />}
        >
          {isSyncing ? 'Syncing...' : 'Refresh Data'}
        </Button>
        {getSyncStatusBadge()}
      </div>
    );
  }

  return (
    <Card title="Live Data Management" subtitle="Sync with FPL API for latest data">
      <div className="space-y-6">
        {/* Current Status */}
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium text-white">Data Status</h3>
            <p className="text-sm text-dark-400">Last updated: {getLastUpdateTime()}</p>
          </div>
          {getSyncStatusBadge()}
        </div>

        {/* Database Stats */}
        {showStats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-100 dark:bg-dark-800 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {statsLoading ? '...' : dbStats?.teams || 0}
              </div>
              <div className="text-sm text-gray-600 dark:text-dark-400">Teams</div>
            </div>

            <div className="bg-gray-100 dark:bg-dark-800 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {statsLoading ? '...' : dbStats?.players || 0}
              </div>
              <div className="text-sm text-gray-600 dark:text-dark-400">Players</div>
            </div>

            <div className="bg-gray-100 dark:bg-dark-800 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {statsLoading ? '...' : dbStats?.fixtures || 0}
              </div>
              <div className="text-sm text-gray-600 dark:text-dark-400">Fixtures</div>
            </div>

            <div className="bg-gray-100 dark:bg-dark-800 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                GW{statsLoading ? '...' : dbStats?.current_gameweek || 1}
              </div>
              <div className="text-sm text-gray-600 dark:text-dark-400">Current</div>
            </div>
          </div>
        )}

        {/* Sync Actions */}
        <div className="space-y-4">
          <div className="flex items-center space-x-4">
            <Button
              variant="primary"
              onClick={() => handleSyncData(false)}
              disabled={isSyncing}
              icon={isSyncing ? <ClockIcon className="h-4 w-4 animate-spin" /> : <ArrowPathIcon className="h-4 w-4" />}
            >
              {isSyncing ? 'Syncing Data...' : 'Sync Latest Data'}
            </Button>
            
            <Button
              variant="secondary"
              onClick={() => handleSyncData(true)}
              disabled={isSyncing}
              icon={<ArrowPathIcon className="h-4 w-4" />}
            >
              Force Full Sync
            </Button>
          </div>

          <div className="text-sm text-dark-400">
            <p>• <strong>Sync Latest Data:</strong> Updates players, fixtures, and gameweek data</p>
            <p>• <strong>Force Full Sync:</strong> Complete refresh of all data from FPL API</p>
          </div>
        </div>

        {/* Last Sync Result */}
        {lastSyncResult && (
          <div className={`p-4 rounded-lg border ${
            lastSyncResult.success 
              ? 'bg-success-900/20 border-success-700' 
              : 'bg-danger-900/20 border-danger-700'
          }`}>
            <div className="flex items-center space-x-2">
              {lastSyncResult.success ? (
                <CheckCircleIcon className="h-5 w-5 text-success-400" />
              ) : (
                <ExclamationTriangleIcon className="h-5 w-5 text-danger-400" />
              )}
              <span className={`font-medium ${
                lastSyncResult.success ? 'text-success-400' : 'text-danger-400'
              }`}>
                {lastSyncResult.message}
              </span>
            </div>
            <p className="text-xs text-dark-400 mt-1">
              {lastSyncResult.timestamp.toLocaleString()}
            </p>
          </div>
        )}

        {/* Data Sources */}
        <div className="bg-dark-800 rounded-lg p-4">
          <h4 className="text-md font-medium text-white mb-2 flex items-center">
            <ChartBarIcon className="h-4 w-4 text-primary-500 mr-2" />
            Data Sources
          </h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-dark-400">FPL API:</span>
              <span className="text-success-400">Live</span>
            </div>
            <div className="flex justify-between">
              <span className="text-dark-400">Player Stats:</span>
              <span className="text-success-400">Real-time</span>
            </div>
            <div className="flex justify-between">
              <span className="text-dark-400">Fixtures:</span>
              <span className="text-success-400">Current season</span>
            </div>
            <div className="flex justify-between">
              <span className="text-dark-400">Historical Data:</span>
              <span className="text-primary-400">2023-24, 2024-25</span>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default DataSync;
