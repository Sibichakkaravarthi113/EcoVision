import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './layouts/AppLayout';
import Overview from './pages/Overview';
import AirQuality from './pages/AirQuality';
import WaterQuality from './pages/WaterQuality';
import GreenCoverage from './pages/GreenCoverage';
import WasteManagement from './pages/WasteManagement';
import NoisePollution from './pages/NoisePollution';
import TrafficCongestion from './pages/TrafficCongestion';
import IndustrialActivity from './pages/IndustrialActivity';
import ClimateConditions from './pages/ClimateConditions';
import EcoVisionAI from './pages/EcoVisionAI';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<AppLayout />}>
        <Route index element={<Navigate to="/overview" replace />} />
        <Route path="overview" element={<Overview />} />
        <Route path="air-quality" element={<AirQuality />} />
        <Route path="water-quality" element={<WaterQuality />} />
        <Route path="green-coverage" element={<GreenCoverage />} />
        <Route path="waste-management" element={<WasteManagement />} />
        <Route path="noise-pollution" element={<NoisePollution />} />
        <Route path="traffic" element={<TrafficCongestion />} />
        <Route path="industrial" element={<IndustrialActivity />} />
        <Route path="climate" element={<ClimateConditions />} />
        <Route path="chat" element={<EcoVisionAI />} />
        <Route path="*" element={<Navigate to="/overview" replace />} />
      </Route>
    </Routes>
  );
}
