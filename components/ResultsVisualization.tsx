'use client';

import { SimulationResult } from '@/lib/heatingLoad';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface ResultsVisualizationProps {
  results: SimulationResult;
}

export default function ResultsVisualization({ results }: ResultsVisualizationProps) {
  const chartData = results.hourlyResults.map((result) => ({
    hour: `${result.hour}:00`,
    'Conductive Loss': Math.round(result.conductiveLoss),
    'Ventilation Loss': Math.round(result.ventilationLoss),
    'Solar Gain': Math.round(result.solarGain),
    'Longwave Radiation': Math.round(result.longwaveRadiation),
    'Net Heating Load': Math.round(result.netLoad),
    'Outdoor Temp': result.outdoorTemp.toFixed(1),
    'Solar Radiation': Math.round(result.solarRadiation),
  }));

  const cardStyle = {
    background: 'white',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    marginBottom: '20px',
  };

  const titleStyle = {
    fontSize: '20px',
    fontWeight: '600',
    marginBottom: '16px',
    color: '#1f2937',
  };

  const summaryStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '16px',
    marginBottom: '24px',
  };

  const summaryItemStyle = {
    background: '#f3f4f6',
    padding: '16px',
    borderRadius: '8px',
    textAlign: 'center' as const,
  };

  const summaryValueStyle = {
    fontSize: '28px',
    fontWeight: '700',
    color: '#2563eb',
    marginBottom: '4px',
  };

  const summaryLabelStyle = {
    fontSize: '14px',
    color: '#6b7280',
  };

  return (
    <div>
      <div style={cardStyle}>
        <h3 style={titleStyle}>Summary</h3>
        <div style={summaryStyle}>
          <div style={summaryItemStyle}>
            <div style={summaryValueStyle}>{results.totalHeatingLoad.toFixed(2)}</div>
            <div style={summaryLabelStyle}>Total Heating Load (kWh/day)</div>
          </div>
          <div style={summaryItemStyle}>
            <div style={summaryValueStyle}>{(results.peakLoad / 1000).toFixed(2)}</div>
            <div style={summaryLabelStyle}>Peak Load (kW)</div>
          </div>
          <div style={summaryItemStyle}>
            <div style={summaryValueStyle}>{(results.averageLoad / 1000).toFixed(2)}</div>
            <div style={summaryLabelStyle}>Average Load (kW)</div>
          </div>
        </div>
      </div>

      <div style={cardStyle}>
        <h3 style={titleStyle}>Hourly Heating Load</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="hour" interval={2} />
            <YAxis label={{ value: 'Power (W)', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="Net Heating Load" stroke="#ef4444" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div style={cardStyle}>
        <h3 style={titleStyle}>Heat Loss and Gain Components</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="hour" interval={2} />
            <YAxis label={{ value: 'Power (W)', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            <Bar dataKey="Conductive Loss" fill="#3b82f6" />
            <Bar dataKey="Ventilation Loss" fill="#8b5cf6" />
            <Bar dataKey="Solar Gain" fill="#f59e0b" />
            <Bar dataKey="Longwave Radiation" fill="#10b981" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div style={cardStyle}>
        <h3 style={titleStyle}>Climate Data</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="hour" interval={2} />
            <YAxis 
              yAxisId="left"
              label={{ value: 'Temperature (°C)', angle: -90, position: 'insideLeft' }} 
            />
            <YAxis 
              yAxisId="right" 
              orientation="right"
              label={{ value: 'Solar Radiation (W/m²)', angle: 90, position: 'insideRight' }} 
            />
            <Tooltip />
            <Legend />
            <Line yAxisId="left" type="monotone" dataKey="Outdoor Temp" stroke="#ef4444" strokeWidth={2} />
            <Line yAxisId="right" type="monotone" dataKey="Solar Radiation" stroke="#f59e0b" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
