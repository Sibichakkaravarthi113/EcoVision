import React, { createContext, useContext, useState, useEffect } from 'react';

const DemoModeContext = createContext();

export function DemoModeProvider({ children }) {
  const [demoMode, setDemoModeState] = useState(() => {
    try {
      const saved = localStorage.getItem('ecovision_demo_mode');
      return saved !== null ? JSON.parse(saved) : false;
    } catch {
      return false;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem('ecovision_demo_mode', JSON.stringify(demoMode));
    } catch (e) {
      console.warn('Failed to persist demo mode:', e);
    }
  }, [demoMode]);

  const toggleDemoMode = () => {
    setDemoModeState(prev => !prev);
  };

  const setDemoMode = (val) => {
    setDemoModeState(Boolean(val));
  };

  return (
    <DemoModeContext.Provider value={{ demoMode, setDemoMode, toggleDemoMode }}>
      {children}
    </DemoModeContext.Provider>
  );
}

export function useDemoMode() {
  const context = useContext(DemoModeContext);
  if (!context) {
    throw new Error('useDemoMode must be used within a DemoModeProvider');
  }
  return context;
}
