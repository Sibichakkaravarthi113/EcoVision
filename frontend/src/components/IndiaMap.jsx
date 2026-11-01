import React, { useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Tooltip, useMap } from 'react-leaflet';
import L from 'leaflet';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// Fix leaflet default icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

// Component to dynamically re-center map when center/zoom props update
function ChangeView({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    if (center && Array.isArray(center) && center.length === 2 && !isNaN(center[0]) && !isNaN(center[1])) {
      map.setView(center, zoom);
    }
  }, [center, zoom, map]);
  return null;
}

export default function IndiaMap({
  markers = [],
  height = 420,
  center = [20.5937, 78.9629],
  zoom = 5,
  title = 'Geographic Environmental Map'
}) {
  // Filter out any markers with missing or invalid lat/lng
  const validMarkers = (markers || []).filter((m) => {
    return (
      m &&
      typeof m.lat === 'number' &&
      !isNaN(m.lat) &&
      typeof m.lng === 'number' &&
      !isNaN(m.lng) &&
      m.lat !== 0 &&
      m.lng !== 0
    );
  });

  return (
    <div className="data-card" style={{ padding: 0, overflow: 'hidden' }}>
      {title && (
        <div style={{ padding: '0.9rem 1.25rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 className="data-card-title" style={{ fontSize: '0.95rem' }}>{title}</h3>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {validMarkers.length} Monitoring Station{validMarkers.length === 1 ? '' : 's'}
          </span>
        </div>
      )}
      <div className="map-wrapper" style={{ height: `${height}px`, width: '100%', borderRadius: 0, border: 'none' }}>
        <MapContainer
          center={center}
          zoom={zoom}
          scrollWheelZoom={false}
          style={{ height: '100%', width: '100%' }}
        >
          <ChangeView center={center} zoom={zoom} />
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {validMarkers.map((marker, index) => {
            const markerColor = marker.color || '#10b981';
            return (
              <CircleMarker
                key={`marker-${index}-${marker.lat}-${marker.lng}`}
                center={[marker.lat, marker.lng]}
                radius={marker.radius || 8}
                pathOptions={{
                  fillColor: markerColor,
                  fillOpacity: 0.85,
                  color: '#ffffff',
                  weight: 2
                }}
              >
                {marker.label && (
                  <Tooltip direction="top" offset={[0, -6]} opacity={0.9}>
                    <span>{marker.label}</span>
                  </Tooltip>
                )}
                <Popup>
                  <div style={{ padding: '4px', minWidth: '150px' }}>
                    <h4 style={{ margin: '0 0 6px 0', fontSize: '0.9rem', color: '#0f2419', borderBottom: '1px solid #e2e8f0', paddingBottom: '4px' }}>
                      {marker.title || marker.label || 'Station Record'}
                    </h4>
                    {marker.value !== undefined && (
                      <p style={{ margin: '3px 0', fontSize: '0.85rem', fontWeight: 600, color: markerColor }}>
                        Value: {marker.value} {marker.unit || ''}
                      </p>
                    )}
                    {marker.status && (
                      <p style={{ margin: '3px 0', fontSize: '0.8rem', color: '#475569' }}>
                        Status: <strong>{marker.status}</strong>
                      </p>
                    )}
                    {marker.popup && typeof marker.popup === 'string' && (
                      <p style={{ margin: '3px 0', fontSize: '0.8rem', color: '#64748b' }}>
                        {marker.popup}
                      </p>
                    )}
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}
        </MapContainer>
      </div>
    </div>
  );
}
