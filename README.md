# EKhu - Building Heating Load Simulator

AI Based Sustainable Building Planning Class Assignment: Building Heating Load Calculation and Simulation Web Application

## Overview

EKhu is a comprehensive web-based simulation tool that calculates and visualizes building heating loads by integrating real-time climate data via interactive maps. The application performs steady-state thermal analysis and hourly time-based simulations with both graphical and tabular outputs.

## Features

### 🗺️ Interactive Location Selection
- Interactive map using OpenStreetMap and Leaflet
- Click anywhere on the map to select a location for climate data
- Real-time coordinate display

### 🏢 Building Parameters
The application allows you to configure:

**Building Envelope:**
- Wall area and U-value
- Roof area and U-value  
- Floor area and U-value

**Windows:**
- Window area and U-value
- Solar Heat Gain Coefficient (SHGC)

**Ventilation:**
- Ventilation rate (Air Changes per Hour)
- Building volume

**Indoor Conditions:**
- Indoor temperature setpoint

### 🔬 Heating Load Calculations

The simulator performs comprehensive thermal analysis including:

1. **Conductive Heat Loss**: Calculates heat loss through walls, roof, floor, and windows based on U-values and temperature difference
2. **Ventilation Heat Loss**: Computes heat loss due to air infiltration based on ventilation rate and air properties
3. **Solar Heat Gain**: Determines solar radiation gains through windows using SHGC
4. **Longwave Radiation**: Accounts for longwave radiation heat exchange using Stefan-Boltzmann law
5. **Steady-State Analysis**: Performs instantaneous thermal balance calculations
6. **Hourly Simulation**: Runs 24-hour time-based simulation with hourly resolution

### 📊 Visualization

**Summary Statistics:**
- Total heating load (kWh/day)
- Peak load (kW)
- Average load (kW)

**Graphical Outputs:**
- Hourly heating load line chart
- Heat loss and gain components bar chart
- Climate data visualization (temperature and solar radiation)

**Tabular Output:**
- Detailed hourly data table with all parameters

## Technology Stack

- **Framework**: Next.js 16 with React 19
- **Language**: TypeScript
- **Mapping**: Leaflet with React-Leaflet
- **Charting**: Recharts
- **Styling**: Inline CSS with responsive design

## Getting Started

### Prerequisites
- Node.js 18+ and npm

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

The application will be available at `http://localhost:3000`

## Usage

1. **Select Location**: Click on the map to select a location (default: Seoul, South Korea)
2. **Configure Building**: Enter building parameters including envelope properties, window specifications, ventilation rate, and indoor temperature
3. **Run Simulation**: Click "Run Simulation" to perform the heating load calculation
4. **View Results**: Review the summary statistics, charts, and detailed hourly data table

## Physics and Calculations

### Conductive Heat Loss
```
Q_cond = Σ(A_i × U_i × ΔT)
```
Where:
- A_i = Surface area (m²)
- U_i = U-value (W/m²·K)
- ΔT = Temperature difference (K)

### Ventilation Heat Loss
```
Q_vent = ṁ × c_p × ΔT
ṁ = ρ × V × ACH / 3600
```
Where:
- ρ = Air density (1.2 kg/m³)
- c_p = Specific heat of air (1005 J/kg·K)
- V = Building volume (m³)
- ACH = Air changes per hour

### Solar Heat Gain
```
Q_solar = A_window × SHGC × I
```
Where:
- A_window = Window area (m²)
- SHGC = Solar heat gain coefficient
- I = Solar radiation (W/m²)

### Longwave Radiation
```
Q_lw = A × ε × σ × (T_indoor⁴ - T_sky⁴)
```
Where:
- ε = Emissivity
- σ = Stefan-Boltzmann constant (5.67×10⁻⁸ W/m²·K⁴)
- T = Temperature (K)

## Project Structure

```
EKhu/
├── app/
│   ├── globals.css          # Global styles
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Main page
├── components/
│   ├── BuildingInputForm.tsx      # Building parameter inputs
│   ├── LocationMap.tsx            # Interactive map component
│   ├── ResultsVisualization.tsx   # Charts and graphs
│   └── ResultsTable.tsx           # Data table
├── lib/
│   └── heatingLoad.ts       # Calculation engine
├── public/                   # Static assets
├── next.config.js           # Next.js configuration
├── tsconfig.json            # TypeScript configuration
└── package.json             # Dependencies
```

## Future Enhancements

Potential improvements for future versions:
- Integration with real weather APIs (e.g., OpenWeatherMap)
- Support for multiple building zones
- Annual energy analysis
- HVAC system sizing recommendations
- Export results to PDF/Excel
- Building geometry visualization
- Cooling load calculations
- Energy cost analysis

## License

ISC

## Author

HJSmiley - AI Based Sustainable Building Planning Class Assignment
