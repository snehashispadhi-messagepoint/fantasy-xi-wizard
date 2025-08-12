import React from 'react';
import { 
  Bars3Icon, 
  BellIcon, 
  MagnifyingGlassIcon,
  SunIcon,
  MoonIcon
} from '@heroicons/react/24/outline';
import { useTheme } from '../../context/ThemeContext';
import { useData } from '../../context/DataContext';
import DataSync from '../Admin/DataSync';

const Header = ({ onMenuClick }) => {
  const { darkMode, toggleDarkMode } = useTheme();
  const { currentGameweek, nextDeadline } = useData();

  const formatDeadline = (deadline) => {
    if (!deadline) return 'No upcoming deadline';
    
    const deadlineDate = new Date(deadline);
    const now = new Date();
    const diffMs = deadlineDate - now;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    
    if (diffMs < 0) return 'Deadline passed';
    if (diffHours < 24) return `${diffHours}h ${diffMinutes}m`;
    
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ${diffHours % 24}h`;
  };

  return (
    <header className="bg-dark-900 border-b border-dark-700 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left side */}
        <div className="flex items-center space-x-4">
          {/* Mobile menu button */}
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 rounded-lg text-dark-400 hover:text-white hover:bg-dark-800 transition-colors"
          >
            <Bars3Icon className="h-6 w-6" />
          </button>
          
          {/* Logo and title */}
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">FX</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Fantasy XI Wizard</h1>
              <p className="text-sm text-dark-400">AI-Powered FPL Analytics</p>
            </div>
          </div>
        </div>

        {/* Center - Search bar */}
        <div className="hidden md:flex flex-1 max-w-md mx-8">
          <div className="relative w-full">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-dark-400" />
            </div>
            <input
              type="text"
              placeholder="Search players, teams..."
              className="block w-full pl-10 pr-3 py-2 border border-dark-600 rounded-lg bg-dark-800 text-white placeholder-dark-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center space-x-4">
          {/* Gameweek info */}
          <div className="hidden sm:flex items-center space-x-4 text-sm">
            <div className="text-center">
              <p className="text-dark-400">Current GW</p>
              <p className="text-white font-semibold">{currentGameweek || '--'}</p>
            </div>
            <div className="text-center">
              <p className="text-dark-400">Next Deadline</p>
              <p className="text-white font-semibold">{formatDeadline(nextDeadline)}</p>
            </div>
          </div>

          {/* Data Sync */}
          <DataSync compact={true} showStats={false} />

          {/* Theme toggle */}
          <button
            onClick={toggleDarkMode}
            className="p-2 rounded-lg text-dark-400 hover:text-white hover:bg-dark-800 transition-colors"
          >
            {darkMode ? (
              <SunIcon className="h-5 w-5" />
            ) : (
              <MoonIcon className="h-5 w-5" />
            )}
          </button>

          {/* Notifications */}
          <button className="p-2 rounded-lg text-dark-400 hover:text-white hover:bg-dark-800 transition-colors relative">
            <BellIcon className="h-5 w-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-primary-500 rounded-full"></span>
          </button>

          {/* User menu */}
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-full flex items-center justify-center">
              <span className="text-white font-semibold text-sm">U</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
