import React from 'react';

const TeamBadge = ({ 
  team, 
  size = 'md', 
  showName = false, 
  className = '' 
}) => {
  if (!team) {
    return (
      <div className={`flex items-center justify-center bg-dark-600 rounded-full ${getSizeClasses(size)} ${className}`}>
        <span className={`font-bold text-dark-400 ${getTextSizeClasses(size)}`}>
          ???
        </span>
      </div>
    );
  }

  const getTeamColor = (teamName) => {
    // Define team colors based on real team colors
    const teamColors = {
      'Arsenal': 'bg-red-600',
      'Aston Villa': 'bg-purple-600',
      'Bournemouth': 'bg-red-500',
      'Brentford': 'bg-red-500',
      'Brighton': 'bg-blue-500',
      'Burnley': 'bg-purple-700',
      'Chelsea': 'bg-blue-600',
      'Crystal Palace': 'bg-blue-500',
      'Everton': 'bg-blue-600',
      'Fulham': 'bg-gray-700',
      'Leeds': 'bg-yellow-500',
      'Liverpool': 'bg-red-600',
      'Man City': 'bg-sky-500',
      'Man Utd': 'bg-red-600',
      'Newcastle': 'bg-gray-800',
      'Nott\'m Forest': 'bg-red-700',
      'Sunderland': 'bg-red-500',
      'Spurs': 'bg-gray-100',
      'West Ham': 'bg-purple-800',
      'Wolves': 'bg-orange-500'
    };
    
    return teamColors[teamName] || 'bg-primary-600';
  };

  const getTextColor = (teamName) => {
    // White text for dark backgrounds, dark text for light backgrounds
    const lightBackgrounds = ['Spurs', 'Leeds'];
    return lightBackgrounds.includes(teamName) ? 'text-gray-900' : 'text-white';
  };

  const getShortName = (team) => {
    if (team.short_name) {
      return team.short_name;
    }
    
    // Fallback to creating short name from full name
    const shortNames = {
      'Arsenal': 'ARS',
      'Aston Villa': 'AVL',
      'Bournemouth': 'BOU',
      'Brentford': 'BRE',
      'Brighton': 'BHA',
      'Burnley': 'BUR',
      'Chelsea': 'CHE',
      'Crystal Palace': 'CRY',
      'Everton': 'EVE',
      'Fulham': 'FUL',
      'Leeds': 'LEE',
      'Liverpool': 'LIV',
      'Man City': 'MCI',
      'Man Utd': 'MUN',
      'Newcastle': 'NEW',
      'Nott\'m Forest': 'NFO',
      'Sunderland': 'SUN',
      'Spurs': 'TOT',
      'West Ham': 'WHU',
      'Wolves': 'WOL'
    };
    
    return shortNames[team.name] || team.name?.substring(0, 3).toUpperCase() || 'TBD';
  };

  const teamColor = getTeamColor(team.name);
  const textColor = getTextColor(team.name);
  const shortName = getShortName(team);

  if (showName) {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <div className={`flex items-center justify-center rounded-full ${teamColor} ${getSizeClasses(size)}`}>
          <span className={`font-bold ${textColor} ${getTextSizeClasses(size)}`}>
            {shortName}
          </span>
        </div>
        <span className="text-white font-medium text-sm">{team.name}</span>
      </div>
    );
  }

  return (
    <div 
      className={`flex items-center justify-center rounded-full ${teamColor} ${getSizeClasses(size)} ${className}`}
      title={team.name}
    >
      <span className={`font-bold ${textColor} ${getTextSizeClasses(size)}`}>
        {shortName}
      </span>
    </div>
  );
};

const getSizeClasses = (size) => {
  switch (size) {
    case 'xs': return 'w-6 h-6';
    case 'sm': return 'w-8 h-8';
    case 'md': return 'w-10 h-10';
    case 'lg': return 'w-12 h-12';
    case 'xl': return 'w-16 h-16';
    default: return 'w-10 h-10';
  }
};

const getTextSizeClasses = (size) => {
  switch (size) {
    case 'xs': return 'text-xs';
    case 'sm': return 'text-xs';
    case 'md': return 'text-sm';
    case 'lg': return 'text-base';
    case 'xl': return 'text-lg';
    default: return 'text-sm';
  }
};

export default TeamBadge;
