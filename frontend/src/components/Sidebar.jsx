import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Wind,
  Droplets,
  Trees,
  Trash2,
  Volume2,
  Car,
  Factory,
  CloudSun,
  Bot,
  Leaf,
  ShieldCheck,
  ShieldAlert
} from 'lucide-react';
import { useDemoMode } from '../context/DemoModeContext';

export default function Sidebar() {
  const { demoMode, toggleDemoMode } = useDemoMode();

  const navItems = [
    { name: 'Overview', path: '/overview', icon: LayoutDashboard },
    { name: 'Air Quality', path: '/air-quality', icon: Wind },
    { name: 'Water Quality', path: '/water-quality', icon: Droplets },
    { name: 'Green Coverage', path: '/green-coverage', icon: Trees },
    { name: 'Waste Management', path: '/waste-management', icon: Trash2 },
    { name: 'Noise Pollution', path: '/noise-pollution', icon: Volume2 },
    { name: 'Traffic Congestion', path: '/traffic', icon: Car },
    { name: 'Industrial Activity', path: '/industrial', icon: Factory },
    { name: 'Climate Conditions', path: '/climate', icon: CloudSun },
    { name: 'EcoVision AI', path: '/chat', icon: Bot },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">
          <Leaf size={22} />
        </div>
        <div className="sidebar-logo-text">
          <h1>EcoVision</h1>
          <span>Environmental Intelligence</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => (isActive ? 'active' : '')}
            >
              <Icon size={19} />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <button
          type="button"
          onClick={toggleDemoMode}
          className={`btn-demo-toggle ${demoMode ? 'active' : ''}`}
          title="Toggle synthetic demonstration data"
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            {demoMode ? <ShieldAlert size={16} /> : <ShieldCheck size={16} />}
            <span>{demoMode ? 'Demo Mode ON' : 'Public Data Mode'}</span>
          </div>
          <span
            style={{
              fontSize: '0.7rem',
              padding: '2px 6px',
              borderRadius: '4px',
              backgroundColor: demoMode ? '#b45309' : '#1e293b'
            }}
          >
            {demoMode ? 'DEMO' : 'LIVE'}
          </span>
        </button>

        <p style={{ fontSize: '0.7rem', color: 'var(--sidebar-muted)', textAlign: 'center', margin: 0 }}>
          &copy; 2026 EcoVision Intelligence
        </p>
      </div>
    </aside>
  );
}
