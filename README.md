# EKhu - Building Heating Load Simulator

AI Based Sustainable Building Planning Class Assignment: Building Heating Load Calculation and Simulation Web Application

## Overview

EKhu is a comprehensive web-based simulation tool that calculates and visualizes building heating loads by integrating real-time climate data via interactive maps. The application features both a Next.js frontend and an advanced Python FastAPI backend with physics-based calculation models. It performs steady-state thermal analysis, transient simulations, radiation heat transfer, and specialized glasshouse calculations with both graphical and tabular outputs.

## Architecture

### Frontend (Next.js + TypeScript)
- Interactive web interface with React 19
- Real-time map-based location selection
- Dynamic visualization with charts and tables
- Dual calculation modes: local TypeScript or Python backend

### Backend (Python + FastAPI)
- Advanced physics-based calculation engine
- RESTful API with 6 specialized endpoints
- Matrix-based solutions for complex heat transfer
- Comprehensive input validation with Pydantic
- OpenAPI/Swagger documentation

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

The simulator offers two calculation engines:

#### Local TypeScript Engine
1. **Conductive Heat Loss**: Calculates heat loss through walls, roof, floor, and windows based on U-values and temperature difference
2. **Ventilation Heat Loss**: Computes heat loss due to air infiltration based on ventilation rate and air properties
3. **Solar Heat Gain**: Determines solar radiation gains through windows using SHGC
4. **Longwave Radiation**: Accounts for longwave radiation heat exchange using Stefan-Boltzmann law
5. **Steady-State Analysis**: Performs instantaneous thermal balance calculations
6. **Hourly Simulation**: Runs 24-hour time-based simulation with hourly resolution

#### Python Backend Engine (Advanced)
1. **Full Simulation**: Comprehensive 24-hour analysis with all physics models
2. **Steady-State Conduction**: Multi-zone heat transfer with matrix solutions
3. **Radiation Heat Transfer**: View factor calculations and radiosity method
4. **Transient Analysis**: RC thermal model with implicit/explicit integration
5. **Glasshouse/Passive Solar**: Specialized iterative solver for passive heating
6. **Climate Data Generation**: Location-based solar position and temperature modeling

### 📊 Visualization

**Summary Statistics:**
- Total heating load (kWh/day)
- Peak load (kW)
- Average load (kW)
- Floor temperature (backend only)
- Radiator output (backend only)

**Graphical Outputs:**
- Hourly heating load line chart
- Heat loss and gain components bar chart
- Climate data visualization (temperature and solar radiation)

**Tabular Output:**
- Detailed hourly data table with all parameters

## Technology Stack

### Frontend
- **Framework**: Next.js 16 with React 19
- **Language**: TypeScript
- **Mapping**: Leaflet with React-Leaflet
- **Charting**: Recharts
- **Styling**: Inline CSS with responsive design

### Backend
- **Framework**: FastAPI 0.104.1
- **Language**: Python 3.11+
- **Scientific Computing**: NumPy 1.26.2, Pandas 2.1.3
- **Validation**: Pydantic 2.5.0
- **Server**: Uvicorn with async support

## Getting Started

### Frontend Setup

#### Prerequisites
- Node.js 18+ and npm

#### Installation

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

### Backend Setup (Optional - for advanced calculations)

#### Prerequisites
- Python 3.11+
- pip

#### Installation

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Start the server
uvicorn main:app --reload
```

The backend API will be available at `http://localhost:8000`

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Docker Deployment

```bash
# Build and run backend
cd backend
docker build -t heating-load-api .
docker run -p 8000:8000 heating-load-api
```

## Usage

1. **Select Location**: Click on the map to select a location (default: Seoul, South Korea)
2. **Configure Building**: Enter building parameters including envelope properties, window specifications, ventilation rate, and indoor temperature
3. **Choose Calculation Engine**: Toggle between Python backend (advanced physics) and local TypeScript (fast, offline)
4. **Run Simulation**: Click "Run Simulation" to perform the heating load calculation
5. **View Results**: Review the summary statistics, charts, and detailed hourly data table

## API Endpoints (Backend)

When the Python backend is running, the following API endpoints are available:

### Full Simulation
**POST** `/api/v1/heating-load/full-simulation`
- Comprehensive 24-hour heating load simulation with all physics models

### Steady-State
**POST** `/api/v1/heating-load/steady-state`
- Calculate steady-state conductive and ventilation losses

### Radiation
**POST** `/api/v1/heating-load/radiation`
- Radiation heat transfer with view factors and radiosity method

### Transient
**POST** `/api/v1/heating-load/transient`
- Transient thermal simulation with RC thermal model

### Glasshouse
**POST** `/api/v1/heating-load/glasshouse`
- Specialized glasshouse/passive solar heating calculation

### Climate Data
**GET** `/api/v1/climate/generate`
- Generate hourly climate data for a given location

See `backend/README.md` for detailed API documentation and request/response examples.

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

### Advanced Physics (Python Backend)

#### Solar Position Calculations
```
δ = 23.45 × sin((360/365)(284 + n))     # Declination angle
H = (hour - 12) × 15°                    # Hour angle
sin(α) = sin(φ)sin(δ) + cos(φ)cos(δ)cos(H)  # Solar elevation
```

#### Radiosity Method
```
[M][J] = [C]
```
Matrix solution for radiation heat transfer with multiple reflections.

#### RC Thermal Model
```
C × dT/dt = (T_outdoor - T_indoor)/R + Φ + Q_solar
```
Transient analysis with thermal capacity and resistance.

## Project Structure

```
EKhu/
├── app/
│   ├── globals.css              # Global styles
│   ├── layout.tsx               # Root layout
│   └── page.tsx                 # Main page with backend integration
├── components/
│   ├── BuildingInputForm.tsx    # Building parameter inputs
│   ├── LocationMap.tsx          # Interactive map component
│   ├── ResultsVisualization.tsx # Charts and graphs
│   └── ResultsTable.tsx         # Data table
├── lib/
│   ├── heatingLoad.ts           # Local TypeScript calculation engine
│   └── api/
│       └── heatingLoadAPI.ts    # Python backend API client
├── backend/                     # Python FastAPI backend
│   ├── main.py                  # FastAPI application
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile               # Docker configuration
│   ├── .env.example             # Environment template
│   ├── models/                  # Pydantic models
│   │   ├── input_models.py      # Input validation
│   │   └── output_models.py     # Response schemas
│   ├── calculations/            # Physics modules
│   │   ├── conduction.py        # Steady-state heat transfer
│   │   ├── radiation.py         # Radiation calculations
│   │   ├── transient.py         # Transient analysis
│   │   ├── glasshouse.py        # Passive solar
│   │   └── climate.py           # Climate data generation
│   ├── utils/                   # Utility modules
│   │   ├── matrix_solver.py     # NumPy matrix operations
│   │   └── solar.py             # Solar position calculations
│   └── README.md                # Backend documentation
├── public/                      # Static assets
├── next.config.js              # Next.js configuration
├── tsconfig.json               # TypeScript configuration
└── package.json                # Frontend dependencies
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
- Advanced transient analysis with weather forecasts
- Building energy certification calculations

## License

ISC

## Author

HJSmiley - AI Based Sustainable Building Planning Class Assignment
