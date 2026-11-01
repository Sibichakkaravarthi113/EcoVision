import React from 'react';
import { AlertCircle } from 'lucide-react';
import { useDemoMode } from '../context/DemoModeContext';

export default function DemoModeBanner() {
  const { demoMode } = useDemoMode();

  if (!demoMode) return null;

  return (
    <div className="demo-banner">
      <AlertCircle size={18} style={{ flexShrink: 0 }} />
      <span>
        DEMO MODE ACTIVE — Showing synthetic demonstration data. Not real environmental measurements.
      </span>
    </div>
  );
}
