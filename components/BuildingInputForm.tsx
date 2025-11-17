'use client';

import { BuildingParams } from '@/lib/heatingLoad';

interface BuildingInputFormProps {
  params: BuildingParams;
  onChange: (params: BuildingParams) => void;
}

export default function BuildingInputForm({ params, onChange }: BuildingInputFormProps) {
  const handleChange = (field: keyof BuildingParams, value: number) => {
    onChange({ ...params, [field]: value });
  };

  const inputStyle = {
    width: '100%',
    padding: '8px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '14px',
  };

  const labelStyle = {
    display: 'block',
    marginBottom: '5px',
    fontWeight: '500',
    fontSize: '14px',
  };

  const sectionStyle = {
    marginBottom: '24px',
  };

  const sectionTitleStyle = {
    fontSize: '18px',
    fontWeight: '600',
    marginBottom: '12px',
    color: '#2563eb',
  };

  const gridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '16px',
  };

  return (
    <div style={{ padding: '20px', background: '#f9fafb', borderRadius: '8px' }}>
      <div style={sectionStyle}>
        <h3 style={sectionTitleStyle}>Building Envelope</h3>
        <div style={gridStyle}>
          <div>
            <label style={labelStyle}>Wall Area (m²)</label>
            <input
              type="number"
              style={inputStyle}
              value={params.wallArea}
              onChange={(e) => handleChange('wallArea', parseFloat(e.target.value))}
              step="0.1"
            />
          </div>
          <div>
            <label style={labelStyle}>Wall U-Value (W/m²·K)</label>
            <input
              type="number"
              style={inputStyle}
              value={params.wallUValue}
              onChange={(e) => handleChange('wallUValue', parseFloat(e.target.value))}
              step="0.01"
            />
          </div>
          <div>
            <label style={labelStyle}>Roof Area (m²)</label>
            <input
              type="number"
              style={inputStyle}
              value={params.roofArea}
              onChange={(e) => handleChange('roofArea', parseFloat(e.target.value))}
              step="0.1"
            />
          </div>
          <div>
            <label style={labelStyle}>Roof U-Value (W/m²·K)</label>
            <input
              type="number"
              style={inputStyle}
              value={params.roofUValue}
              onChange={(e) => handleChange('roofUValue', parseFloat(e.target.value))}
              step="0.01"
            />
          </div>
          <div>
            <label style={labelStyle}>Floor Area (m²)</label>
            <input
              type="number"
              style={inputStyle}
              value={params.floorArea}
              onChange={(e) => handleChange('floorArea', parseFloat(e.target.value))}
              step="0.1"
            />
          </div>
          <div>
            <label style={labelStyle}>Floor U-Value (W/m²·K)</label>
            <input
              type="number"
              style={inputStyle}
              value={params.floorUValue}
              onChange={(e) => handleChange('floorUValue', parseFloat(e.target.value))}
              step="0.01"
            />
          </div>
        </div>
      </div>

      <div style={sectionStyle}>
        <h3 style={sectionTitleStyle}>Windows</h3>
        <div style={gridStyle}>
          <div>
            <label style={labelStyle}>Window Area (m²)</label>
            <input
              type="number"
              style={inputStyle}
              value={params.windowArea}
              onChange={(e) => handleChange('windowArea', parseFloat(e.target.value))}
              step="0.1"
            />
          </div>
          <div>
            <label style={labelStyle}>Window U-Value (W/m²·K)</label>
            <input
              type="number"
              style={inputStyle}
              value={params.windowUValue}
              onChange={(e) => handleChange('windowUValue', parseFloat(e.target.value))}
              step="0.01"
            />
          </div>
          <div>
            <label style={labelStyle}>SHGC (Solar Heat Gain Coefficient)</label>
            <input
              type="number"
              style={inputStyle}
              value={params.shgc}
              onChange={(e) => handleChange('shgc', parseFloat(e.target.value))}
              step="0.01"
              min="0"
              max="1"
            />
          </div>
        </div>
      </div>

      <div style={sectionStyle}>
        <h3 style={sectionTitleStyle}>Ventilation</h3>
        <div style={gridStyle}>
          <div>
            <label style={labelStyle}>Ventilation Rate (ACH)</label>
            <input
              type="number"
              style={inputStyle}
              value={params.ventilationRate}
              onChange={(e) => handleChange('ventilationRate', parseFloat(e.target.value))}
              step="0.1"
            />
          </div>
          <div>
            <label style={labelStyle}>Building Volume (m³)</label>
            <input
              type="number"
              style={inputStyle}
              value={params.buildingVolume}
              onChange={(e) => handleChange('buildingVolume', parseFloat(e.target.value))}
              step="1"
            />
          </div>
        </div>
      </div>

      <div style={sectionStyle}>
        <h3 style={sectionTitleStyle}>Indoor Conditions</h3>
        <div style={gridStyle}>
          <div>
            <label style={labelStyle}>Indoor Temperature (°C)</label>
            <input
              type="number"
              style={inputStyle}
              value={params.indoorTemp}
              onChange={(e) => handleChange('indoorTemp', parseFloat(e.target.value))}
              step="0.5"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
