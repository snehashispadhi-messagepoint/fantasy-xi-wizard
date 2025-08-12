import React from 'react';

const Card = ({ 
  children, 
  className = '', 
  header = null, 
  title = null,
  subtitle = null,
  actions = null,
  padding = true,
  ...props 
}) => {
  return (
    <div className={`card ${className}`} {...props}>
      {(header || title || subtitle || actions) && (
        <div className="card-header flex items-center justify-between">
          <div>
            {title && (
              <h3 className="text-lg font-semibold text-white">{title}</h3>
            )}
            {subtitle && (
              <p className="text-sm text-dark-400 mt-1">{subtitle}</p>
            )}
            {header}
          </div>
          {actions && (
            <div className="flex items-center space-x-2">
              {actions}
            </div>
          )}
        </div>
      )}
      
      <div className={padding ? 'card-body' : ''}>
        {children}
      </div>
    </div>
  );
};

export default Card;
