'use client';

import { SimulationResult } from '@/lib/heatingLoad';

interface ResultsTableProps {
  results: SimulationResult;
}

export default function ResultsTable({ results }: ResultsTableProps) {
  const tableStyle = {
    width: '100%',
    borderCollapse: 'collapse' as const,
    fontSize: '14px',
  };

  const thStyle = {
    background: '#f3f4f6',
    padding: '12px 8px',
    textAlign: 'left' as const,
    fontWeight: '600',
    borderBottom: '2px solid #e5e7eb',
  };

  const tdStyle = {
    padding: '10px 8px',
    borderBottom: '1px solid #e5e7eb',
  };

  const cardStyle = {
    background: 'white',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    overflowX: 'auto' as const,
  };

  const titleStyle = {
    fontSize: '20px',
    fontWeight: '600',
    marginBottom: '16px',
    color: '#1f2937',
  };

  return (
    <div style={cardStyle}>
      <h3 style={titleStyle}>Hourly Data Table</h3>
      <table style={tableStyle}>
        <thead>
          <tr>
            <th style={thStyle}>Hour</th>
            <th style={thStyle}>Outdoor Temp (°C)</th>
            <th style={thStyle}>Solar Rad. (W/m²)</th>
            <th style={thStyle}>Conductive Loss (W)</th>
            <th style={thStyle}>Ventilation Loss (W)</th>
            <th style={thStyle}>Solar Gain (W)</th>
            <th style={thStyle}>Longwave Rad. (W)</th>
            <th style={thStyle}>Net Heating Load (W)</th>
          </tr>
        </thead>
        <tbody>
          {results.hourlyResults.map((result) => (
            <tr key={result.hour}>
              <td style={tdStyle}>{result.hour}:00</td>
              <td style={tdStyle}>{result.outdoorTemp.toFixed(1)}</td>
              <td style={tdStyle}>{Math.round(result.solarRadiation)}</td>
              <td style={tdStyle}>{Math.round(result.conductiveLoss)}</td>
              <td style={tdStyle}>{Math.round(result.ventilationLoss)}</td>
              <td style={tdStyle}>{Math.round(result.solarGain)}</td>
              <td style={tdStyle}>{Math.round(result.longwaveRadiation)}</td>
              <td style={tdStyle}>{Math.round(result.netLoad)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
