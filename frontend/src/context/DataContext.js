import React, { createContext, useContext, useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { apiService } from '../services/apiService';

const DataContext = createContext();

export const useData = () => {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error('useData must be used within a DataProvider');
  }
  return context;
};

export const DataProvider = ({ children }) => {
  const [currentGameweek, setCurrentGameweek] = useState(null);
  const [nextDeadline, setNextDeadline] = useState(null);
  const [selectedPlayers, setSelectedPlayers] = useState([]);
  const [filters, setFilters] = useState({
    position: '',
    team: '',
    minPrice: '',
    maxPrice: '',
    sortBy: 'total_points',
    sortOrder: 'desc'
  });

  // Fetch current gameweek with live updates
  const { data: gameweekData } = useQuery(
    'current-gameweek',
    () => apiService.getCurrentGameweek(),
    {
      refetchInterval: 2 * 60 * 1000, // Refetch every 2 minutes for live updates
      staleTime: 1 * 60 * 1000, // Consider data stale after 1 minute
      onSuccess: (data) => {
        if (data?.current_gameweek) {
          setCurrentGameweek(data.current_gameweek);
        }
      }
    }
  );

  // Fetch next deadline with frequent updates
  const { data: deadlineData } = useQuery(
    'next-deadline',
    () => apiService.getNextDeadline(),
    {
      refetchInterval: 30 * 1000, // Refetch every 30 seconds for deadline countdown
      staleTime: 15 * 1000, // Consider data stale after 15 seconds
      onSuccess: (data) => {
        if (data?.next_deadline) {
          setNextDeadline(data.next_deadline);
        }
      }
    }
  );

  // Player selection management
  const addSelectedPlayer = (player) => {
    setSelectedPlayers(prev => {
      if (prev.find(p => p.id === player.id)) {
        return prev; // Player already selected
      }
      if (prev.length >= 3) {
        return [...prev.slice(1), player]; // Keep only last 3 players
      }
      return [...prev, player];
    });
  };

  const removeSelectedPlayer = (playerId) => {
    setSelectedPlayers(prev => prev.filter(p => p.id !== playerId));
  };

  const clearSelectedPlayers = () => {
    setSelectedPlayers([]);
  };

  // Filter management
  const updateFilters = (newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  };

  const resetFilters = () => {
    setFilters({
      position: '',
      team: '',
      minPrice: '',
      maxPrice: '',
      sortBy: 'total_points',
      sortOrder: 'desc'
    });
  };

  // Utility functions
  const getPositionName = (elementType) => {
    const positions = {
      1: 'GK',
      2: 'DEF',
      3: 'MID',
      4: 'FWD'
    };
    return positions[elementType] || 'Unknown';
  };

  const formatPrice = (price) => {
    return (price / 10).toFixed(1);
  };

  const formatDeadline = (deadline) => {
    if (!deadline) return null;
    
    const deadlineDate = new Date(deadline);
    const now = new Date();
    const diffMs = deadlineDate - now;
    
    if (diffMs < 0) return 'Deadline passed';
    
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    
    if (diffHours < 24) {
      return `${diffHours}h ${diffMinutes}m`;
    }
    
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ${diffHours % 24}h`;
  };

  const value = {
    // Game state
    currentGameweek,
    nextDeadline,
    formattedDeadline: formatDeadline(nextDeadline),
    
    // Player selection
    selectedPlayers,
    addSelectedPlayer,
    removeSelectedPlayer,
    clearSelectedPlayers,
    
    // Filters
    filters,
    updateFilters,
    resetFilters,
    
    // Utility functions
    getPositionName,
    formatPrice,
    formatDeadline,
  };

  return (
    <DataContext.Provider value={value}>
      {children}
    </DataContext.Provider>
  );
};
