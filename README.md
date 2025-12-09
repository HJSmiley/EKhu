# Building Heating Load Calculation Backend

Advanced physics-based Python FastAPI backend for building heating load calculations with support for steady-state, radiation, transient, and glasshouse analysis.

## Features

- **Full Simulation**: Comprehensive 24-hour heating load simulation with all physics models
- **Steady-State Analysis**: Conductive and ventilation heat loss calculations
- **Radiation Heat Transfer**: View factor calculations and radiosity method
- **Transient Analysis**: RC thermal model with time-stepping integration
- **Glasshouse/Passive Solar**: Specialized iterative solver for passive heating systems
- **Real Weather Data**: Open-Meteo API integration for actual weather observations and forecasts
- **Climate Data Generation**: Location-based solar radiation and temperature modeling (synthetic fallback)
- **Natural Ventilation**: Wind-driven and stack effect calculations (NEW)
- **Condensation Analysis**: Glaser method and psychrometric calculations (NEW)

## Installation

### Prerequisites

- **Python 3.12** (권장)
  - Python 3.13은 pandas 등의 라이브러리와 호환성 문제가 있을 수 있습니다
  - Python 3.11도 사용 가능하지만 3.12를 권장합니다
- pip

### Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment with Python 3.12 (recommended)
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
```

**Python 버전 확인:**
```bash
python --version  # Python 3.12.x 확인
```

### Configuration

Edit `.env` file:

```env
PORT=8000
CORS_ORIGINS=http://localhost:3000
LOG_LEVEL=INFO
```

## Running the Server

### Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker

```bash
# Build Docker image
docker build -t heating-load-api .

# Run container
docker run -p 8000:8000 heating-load-api
```

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Full Simulation

**POST** `/api/v1/heating-load/full-simulation`

Comprehensive heating load calculation with all physics models.

**Request Body:**
```json
{
  "building": {
    "wall_area": 150,
    "wall_u_value": 0.35,
    "roof_area": 100,
    "roof_u_value": 0.25,
    "floor_area": 100,
    "floor_u_value": 0.30,
    "window_area": 30,
    "window_u_value": 1.8,
    "shgc": 0.6,
    "ventilation_rate": 0.5,
    "building_volume": 300,
    "indoor_temp": 20,
    "emissivity": 0.85,
    "reflectivity": 0.15,
    "thermal_capacity": 1e7,
    "thermal_resistance": 8e-3
  },
  "climate": {
    "latitude": 37.5665,
    "longitude": 126.9780,
    "day_of_year": 15
  },
  "simulation_options": {
    "include_radiation": true,
    "include_transient": true,
    "timestep_seconds": 3600
  }
}
```

**Response:**
```json
{
  "hourly_results": [
    {
      "hour": 0,
      "outdoor_temp": -5.2,
      "solar_radiation": 0,
      "conductive_loss": 3200,
      "ventilation_loss": 850,
      "solar_gain": 0,
      "longwave_radiation": 120,
      "radiation_heat_transfer": 450,
      "net_load": 4170,
      "indoor_temp_dynamic": 19.8
    }
  ],
  "summary": {
    "total_heating_load_kwh": 85.3,
    "peak_load_w": 5200,
    "average_load_w": 3550,
    "floor_temperature": 18.5,
    "radiator_output": 2800
  }
}
```

### Steady-State Calculation

**POST** `/api/v1/heating-load/steady-state`

Calculate steady-state conductive and ventilation losses.

### Radiation Calculation

**POST** `/api/v1/heating-load/radiation`

Calculate radiation heat transfer with view factors and radiosity method.

### Transient Simulation

**POST** `/api/v1/heating-load/transient`

Simulate transient thermal response using RC thermal model.

### Glasshouse Calculation

**POST** `/api/v1/heating-load/glasshouse`

Specialized calculation for glasshouse/passive solar heating systems.

### Climate Data Generation

**GET** `/api/v1/climate/generate?latitude=37.5665&longitude=126.9780&day_of_year=15&use_api=true`

Generate hourly climate data for a specific location.

**Parameters:**
- `latitude`: 위도 (필수)
- `longitude`: 경도 (필수)
- `day_of_year`: 연중 일수 (1-365, 기본값: 15)
- `use_api`: `true`면 Open-Meteo API 사용, `false`면 합성 데이터 (기본값: true)

**Weather Data Source:**
- **실제 날씨 데이터 (use_api=true)**: Open-Meteo API를 통해 실시간 관측 데이터와 예측 데이터를 가져옵니다
  - 현재 시간까지: 실제 관측 데이터
  - 현재 시간 이후: 예측 데이터
  - 포함 데이터: 온도, 습도, 직달일사량, 산란일사량, 전일사량
- **합성 데이터 (use_api=false 또는 API 실패 시)**: 위도와 시간 기반 수학적 모델로 생성

## Weather Data Integration

### Open-Meteo API

이 백엔드는 무료 Open-Meteo API를 사용하여 실제 날씨 데이터를 가져옵니다 (API 키 불필요).

**데이터 소스:**
- **Archive API**: 과거 관측 데이터 (오늘 00시 ~ 현재 시간)
- **Forecast API**: 예측 데이터 (현재 시간 ~ 다음날 00시)

**제공 데이터:**
- 기온 (°C)
- 상대습도 (%)
- 직달일사량 (W/m²)
- 산란일사량 (W/m²)
- 전일사량 (W/m²)

**Fallback 메커니즘:**
API 요청이 실패하거나 데이터가 불완전한 경우, 자동으로 합성 데이터 생성 모드로 전환됩니다.

## Calculation Methodology

### Conduction Heat Loss

Uses the fundamental heat transfer equation:

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

### Solar Radiation

**Solar Position:**
```
δ = 23.45 × sin((360/365)(284 + n))  # Declination
H = (hour - 12) × 15°                 # Hour angle
sin(α) = sin(φ)sin(δ) + cos(φ)cos(δ)cos(H)  # Elevation
```

**Solar Irradiance:**
```
DNI = I_sc × τ^(AM^0.678)
GHI = DNI × sin(α)
```

Where:
- I_sc = Solar constant (1367 W/m²)
- τ = Atmospheric transmittance (0.7)
- AM = Air mass = 1/sin(α)

### Radiation Heat Transfer

**Stefan-Boltzmann Law:**
```
Q_rad = ε × σ × A × (T₁⁴ - T₂⁴)
```

**Radiosity Method:**
```
[M][J] = [C]
```

Where M is the view factor matrix, J is radiosity, and C is emissive power.

### Transient Analysis

**RC Thermal Model:**
```
C × dT/dt = (T_outdoor - T_indoor) / R + Φ + Q_solar
```

Using implicit (backward Euler) integration for stability.

### Glasshouse Model

Iterative matrix solution for coupled energy balances:
1. Interior: convection + radiation = back loss
2. Glass: solar absorption + radiation = convection
3. Collector: solar absorption = radiation + convection

## Project Structure

```
backend/
├── main.py                    # FastAPI application
├── requirements.txt           # Python dependencies
├── Dockerfile                # Docker configuration
├── .env.example              # Environment template
├── models/
│   ├── __init__.py
│   ├── input_models.py       # Pydantic input validation
│   └── output_models.py      # Response models
├── calculations/
│   ├── __init__.py
│   ├── conduction.py         # Steady-state calculations
│   ├── radiation.py          # Radiation heat transfer
│   ├── transient.py          # Transient thermal analysis
│   ├── glasshouse.py         # Glasshouse calculations
│   └── climate.py            # Climate data (Open-Meteo API + synthetic)
├── utils/
│   ├── __init__.py
│   ├── matrix_solver.py      # NumPy matrix operations
│   └── solar.py              # Solar calculations
└── README.md                 # This file
```

## Testing

Run the API tests:

```bash
# Install test dependencies
pip install pytest pytest-cov httpx

# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

## Example Usage

### Python Client

```python
import requests

# Full simulation
response = requests.post(
    "http://localhost:8000/api/v1/heating-load/full-simulation",
    json={
        "building": {
            "wall_area": 150,
            "wall_u_value": 0.35,
            "roof_area": 100,
            "roof_u_value": 0.25,
            "floor_area": 100,
            "floor_u_value": 0.30,
            "window_area": 30,
            "window_u_value": 1.8,
            "shgc": 0.6,
            "ventilation_rate": 0.5,
            "building_volume": 300,
            "indoor_temp": 20
        },
        "climate": {
            "latitude": 37.5665,
            "longitude": 126.9780,
            "day_of_year": 15
        }
    }
)

results = response.json()
print(f"Total heating load: {results['summary']['total_heating_load_kwh']} kWh")
```

### JavaScript/TypeScript Client

```typescript
const response = await fetch('http://localhost:8000/api/v1/heating-load/full-simulation', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    building: {
      wall_area: 150,
      wall_u_value: 0.35,
      // ... other parameters
    },
    climate: {
      latitude: 37.5665,
      longitude: 126.9780,
      day_of_year: 15
    }
  })
});

const results = await response.json();
console.log(`Total heating load: ${results.summary.total_heating_load_kwh} kWh`);
```

## Physical Constants

- Stefan-Boltzmann constant: σ = 5.67×10⁻⁸ W/m²·K⁴
- Air density: ρ = 1.2 kg/m³
- Specific heat of air: c_p = 1005 J/kg·K
- Solar constant: I_sc = 1367 W/m²
- Atmospheric transmittance: τ = 0.7

## Performance

- Typical response time: < 100ms for full simulation
- Supports concurrent requests
- Can handle 1000+ requests/second with 4 workers

## Troubleshooting

### Common Issues

1. **Port already in use**: Change PORT in .env file
2. **CORS errors**: Add frontend URL to CORS_ORIGINS in .env
3. **Import errors**: Ensure virtual environment is activated
4. **Slow performance**: Increase number of workers or use Docker

### Logging

Check logs for detailed error information:

```bash
# Set log level in .env
LOG_LEVEL=DEBUG
```

## Contributing

1. Follow PEP 8 style guide
2. Add type hints to all functions
3. Write docstrings for new modules
4. Add tests for new features
5. Update documentation

## License

ISC

## Author

HJSmiley - AI Based Sustainable Building Planning Class Assignment
