import React from 'react';

const LoadingSpinner = ({ 
  size = 'md', 
  color = 'primary', 
  text = null,
  className = '' 
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
    xl: 'h-12 w-12'
  };

  const colorClasses = {
    primary: 'border-primary-500',
    white: 'border-white',
    gray: 'border-dark-400'
  };

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <div className="flex flex-col items-center space-y-2">
        <div 
          className={`
            ${sizeClasses[size]} 
            ${colorClasses[color]}
            animate-spin rounded-full border-2 border-t-transparent
          `}
        />
        {text && (
          <p className="text-sm text-dark-400">{text}</p>
        )}
      </div>
    </div>
  );
};

export default LoadingSpinner;
