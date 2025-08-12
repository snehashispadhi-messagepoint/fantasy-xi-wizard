import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { 
  HomeIcon,
  UserGroupIcon,
  BuildingOfficeIcon,
  CalendarDaysIcon,
  ChartBarIcon,
  SparklesIcon,
  ArrowsRightLeftIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

const Sidebar = ({ isOpen, onClose }) => {
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
    { name: 'Players', href: '/players', icon: UserGroupIcon },
    { name: 'Teams', href: '/teams', icon: BuildingOfficeIcon },
    { name: 'Fixtures', href: '/fixtures', icon: CalendarDaysIcon },
    { name: 'Statistics', href: '/statistics', icon: ChartBarIcon },
    { name: 'Compare Players', href: '/compare', icon: ArrowsRightLeftIcon },
    { name: 'AI Recommendations', href: '/recommendations', icon: SparklesIcon },
  ];

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-dark-700">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">FX</span>
          </div>
          <span className="text-white font-semibold">Fantasy XI</span>
        </div>
        
        {/* Close button for mobile */}
        <button
          onClick={onClose}
          className="lg:hidden p-2 rounded-lg text-dark-400 hover:text-white hover:bg-dark-800 transition-colors"
        >
          <XMarkIcon className="h-5 w-5" />
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href;
          return (
            <NavLink
              key={item.name}
              to={item.href}
              onClick={() => onClose()}
              className={`
                sidebar-item group
                ${isActive ? 'active' : ''}
              `}
            >
              <item.icon className="h-5 w-5 mr-3 flex-shrink-0" />
              <span className="truncate">{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-dark-700">
        <div className="bg-dark-800 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
              <SparklesIcon className="h-5 w-5 text-white" />
            </div>
            <div>
              <p className="text-sm font-medium text-white">AI Assistant</p>
              <p className="text-xs text-dark-400">Get smart recommendations</p>
            </div>
          </div>
          <button className="w-full mt-3 btn-primary text-xs py-2">
            Ask AI
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <div className="hidden lg:flex lg:flex-shrink-0">
        <div className="flex flex-col w-64 bg-dark-900 border-r border-dark-700">
          <SidebarContent />
        </div>
      </div>

      {/* Mobile sidebar overlay */}
      {isOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          {/* Overlay */}
          <div 
            className="fixed inset-0 bg-black bg-opacity-50"
            onClick={onClose}
          />
          
          {/* Sidebar */}
          <div className="relative flex flex-col w-64 bg-dark-900 border-r border-dark-700">
            <SidebarContent />
          </div>
        </div>
      )}
    </>
  );
};

export default Sidebar;
