import React from 'react';
import { useLocation } from 'react-router-dom';
import { Sun, Moon, Bell } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import LocationSelector from './LocationSelector';

const ROUTE_TITLES = {
  '/': 'Environmental Overview',
  '/overview': 'Environmental Overview',
  '/air-quality': 'Air Quality Monitoring',
  '/water-quality': 'Water Quality Monitoring',
  '/green-coverage': 'Forest & Green Coverage',
  '/waste-management': 'Waste Management',
  '/noise-pollution': 'Noise Pollution Monitoring',
  '/traffic': 'Traffic Congestion',
  '/industrial': 'Industrial Activity',
  '/climate': 'Climate Conditions',
  '/chat': 'EcoVision AI Assistant'
};

export default function Header() {
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();

  const title = ROUTE_TITLES[location.pathname] || 'EcoVision Platform';

  return (
    <header className="header">
      <div className="header-left">
        <h2 className="header-title">{title}</h2>
      </div>

      <div className="header-center">
        <LocationSelector compact={true} />
      </div>

      <div className="header-right">
        <button
          type="button"
          onClick={toggleTheme}
          className="btn-icon"
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        <button
          type="button"
          className="btn-icon"
          title="Notifications"
          style={{ position: 'relative' }}
        >
          <Bell size={18} />
          <span
            style={{
              position: 'absolute',
              top: '6px',
              right: '6px',
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: 'var(--accent-emerald)'
            }}
          />
        </button>

        <div className="user-avatar" title="EcoVision User">
          EV
        </div>
      </div>
    </header>
  );
}
