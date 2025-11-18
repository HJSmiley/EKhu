'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import BuildingInputForm from '@/components/BuildingInputForm';
import ResultsVisualization from '@/components/ResultsVisualization';
import ResultsTable from '@/components/ResultsTable';
import {
  BuildingParams,
  SimulationResult,
  generateHourlyClimateData,
  runHourlySimulation,
} from '@/lib/heatingLoad';
import {
  calculateHeatingLoad,
  checkBackendHealth,
  type FullSimulationResponse,
} from '@/lib/api/heatingLoadAPI';

// Dynamically import LocationMap to avoid SSR issues with Leaflet
const LocationMap = dynamic(() => import('@/components/LocationMap'), {
  ssr: false,
  loading: () => <div style={{ height: '400px', background: '#f3f4f6', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>Loading map...</div>,
});

export default function Home() {
  const [location, setLocation] = useState({ latitude: 37.5665, longitude: 126.9780 }); // Seoul, South Korea
  const [buildingParams, setBuildingParams] = useState<BuildingParams>({
    wallArea: 150,
    wallUValue: 0.35,
    roofArea: 100,
    roofUValue: 0.25,
    floorArea: 100,
    floorUValue: 0.30,
    windowArea: 30,
    windowUValue: 1.8,
    shgc: 0.6,
    ventilationRate: 0.5,
    buildingVolume: 300,
    indoorTemp: 20,
  });
  const [simulationResults, setSimulationResults] = useState<SimulationResult | null>(null);
  const [useBackend, setUseBackend] = useState(false);
  const [backendAvailable, setBackendAvailable] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Check backend availability on mount
  useEffect(() => {
    checkBackendHealth().then((available) => {
      setBackendAvailable(available);
      setUseBackend(available);
    });
  }, []);

  const handleLocationChange = (lat: number, lng: number) => {
    setLocation({ latitude: lat, longitude: lng });
  };

  const convertBackendResultsToLocal = (backendResults: FullSimulationResponse): SimulationResult => {
    return {
      hourlyResults: backendResults.hourly_results.map((r) => ({
        hour: r.hour,
        outdoorTemp: r.outdoor_temp,
        solarRadiation: r.solar_radiation,
        conductiveLoss: r.conductive_loss,
        ventilationLoss: r.ventilation_loss,
        solarGain: r.solar_gain,
        longwaveRadiation: r.longwave_radiation,
        netLoad: r.net_load,
      })),
      totalHeatingLoad: backendResults.summary.total_heating_load_kwh,
      peakLoad: backendResults.summary.peak_load_w,
      averageLoad: backendResults.summary.average_load_w,
    };
  };

  const handleSimulate = async () => {
    setIsSimulating(true);
    setErrorMessage(null);

    try {
      if (useBackend && backendAvailable) {
        // Use Python backend
        const backendResults = await calculateHeatingLoad(
          buildingParams,
          {
            latitude: location.latitude,
            longitude: location.longitude,
            day_of_year: 15,
          },
          {
            include_radiation: true,
            include_transient: true,
            timestep_seconds: 3600,
          }
        );
        setSimulationResults(convertBackendResultsToLocal(backendResults));
      } else {
        // Use local TypeScript calculations
        const climateData = generateHourlyClimateData(location.latitude, location.longitude);
        const results = runHourlySimulation(buildingParams, climateData);
        setSimulationResults(results);
      }
    } catch (error) {
      console.error('Simulation error:', error);
      setErrorMessage(error instanceof Error ? error.message : 'Simulation failed');
      
      // Fallback to local calculation
      if (useBackend) {
        console.log('Falling back to local calculation');
        const climateData = generateHourlyClimateData(location.latitude, location.longitude);
        const results = runHourlySimulation(buildingParams, climateData);
        setSimulationResults(results);
      }
    } finally {
      setIsSimulating(false);
    }
  };

  // Run initial simulation on mount
  useEffect(() => {
    handleSimulate();
  }, []);

  const containerStyle = {
    minHeight: '100vh',
    background: 'linear-gradient(to bottom, #f9fafb, #ffffff)',
  };

  const headerStyle = {
    background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
    color: 'white',
    padding: '32px 20px',
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
  };

  const titleStyle = {
    fontSize: '36px',
    fontWeight: '700',
    margin: '0 0 8px 0',
    textAlign: 'center' as const,
  };

  const subtitleStyle = {
    fontSize: '16px',
    margin: 0,
    textAlign: 'center' as const,
    opacity: 0.9,
  };

  const mainStyle = {
    maxWidth: '1400px',
    margin: '0 auto',
    padding: '32px 20px',
  };

  const sectionStyle = {
    marginBottom: '32px',
  };

  const sectionTitleStyle = {
    fontSize: '24px',
    fontWeight: '600',
    marginBottom: '16px',
    color: '#1f2937',
  };

  const buttonStyle = {
    background: '#2563eb',
    color: 'white',
    border: 'none',
    padding: '16px 32px',
    fontSize: '16px',
    fontWeight: '600',
    borderRadius: '8px',
    cursor: isSimulating ? 'not-allowed' : 'pointer',
    display: 'block',
    margin: '24px auto',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    opacity: isSimulating ? 0.7 : 1,
  };

  const toggleContainerStyle = {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    gap: '12px',
    marginTop: '16px',
  };

  const toggleLabelStyle = {
    fontSize: '14px',
    color: '#6b7280',
  };

  return (
    <div style={containerStyle}>
      <header style={headerStyle}>
        <h1 style={titleStyle}>EKhu - Building Heating Load Simulator</h1>
        <p style={subtitleStyle}>
          Calculate and visualize heating loads with real-time climate data integration
        </p>
      </header>

      <main style={mainStyle}>
        <section style={sectionStyle}>
          <h2 style={sectionTitleStyle}>📍 Select Location</h2>
          <div style={{ background: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <p style={{ marginTop: 0, marginBottom: '16px', color: '#6b7280' }}>
              Click on the map to select a location for climate data. Current: {location.latitude.toFixed(4)}°N, {location.longitude.toFixed(4)}°E
            </p>
            <LocationMap
              latitude={location.latitude}
              longitude={location.longitude}
              onLocationChange={handleLocationChange}
            />
          </div>
        </section>

        <section style={sectionStyle}>
          <h2 style={sectionTitleStyle}>🏢 Building Parameters</h2>
          <BuildingInputForm params={buildingParams} onChange={setBuildingParams} />
        </section>

        <button style={buttonStyle} onClick={handleSimulate} disabled={isSimulating}>
          {isSimulating ? '⏳ Simulating...' : '🔄 Run Simulation'}
        </button>

        <div style={toggleContainerStyle}>
          <span style={toggleLabelStyle}>
            Calculation Engine: {useBackend ? '🐍 Python Backend' : '📝 Local TypeScript'}
          </span>
          {backendAvailable && (
            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={useBackend}
                onChange={(e) => setUseBackend(e.target.checked)}
                style={{ marginRight: '8px' }}
              />
              Use Python Backend
            </label>
          )}
          {!backendAvailable && (
            <span style={{ ...toggleLabelStyle, color: '#f59e0b' }}>
              ⚠️ Backend unavailable (using local)
            </span>
          )}
        </div>

        {errorMessage && (
          <div style={{
            background: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '8px',
            padding: '12px',
            margin: '16px auto',
            maxWidth: '600px',
            color: '#991b1b',
            fontSize: '14px',
          }}>
            ⚠️ {errorMessage}
          </div>
        )}

        {simulationResults && (
          <>
            <section style={sectionStyle}>
              <h2 style={sectionTitleStyle}>📊 Simulation Results</h2>
              <ResultsVisualization results={simulationResults} />
            </section>

            <section style={sectionStyle}>
              <h2 style={sectionTitleStyle}>📋 Detailed Hourly Data</h2>
              <ResultsTable results={simulationResults} />
            </section>
          </>
        )}
      </main>

      <footer style={{ textAlign: 'center', padding: '32px 20px', color: '#6b7280', borderTop: '1px solid #e5e7eb' }}>
        <p>EKhu - AI Based Sustainable Building Planning Class Assignment</p>
        <p style={{ fontSize: '14px', marginTop: '8px' }}>
          Building Heating Load Calculation and Simulation Web Tool
        </p>
      </footer>
    </div>
  );
}
