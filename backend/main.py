"""FastAPI backend for building heating load calculations."""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging
from typing import List

from models.input_models import (
    FullSimulationRequest,
    SteadyStateRequest,
    RadiationRequest,
    TransientRequest,
    GlasshouseRequest,
    ClimateRequest
)
from models.output_models import (
    FullSimulationResponse,
    SteadyStateResponse,
    RadiationResponse,
    TransientResponse,
    GlasshouseResponse,
    ClimateResponse,
    HourlyResult,
    SimulationSummary,
    ClimateData
)
from calculations.climate import generate_hourly_climate_data
from calculations.conduction import calculate_total_building_loss
from calculations.radiation import (
    calculate_longwave_radiation_to_sky,
    solve_radiation_exchange,
    calculate_floor_temperature_from_radiosity
)
from calculations.transient import (
    simulate_transient_response,
    estimate_thermal_capacity,
    estimate_thermal_resistance
)
from calculations.glasshouse import (
    solve_glasshouse_temperatures,
    calculate_passive_solar_gain
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Building Heating Load API",
    description="Advanced physics-based building heating load calculations",
    version="1.0.0"
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Building Heating Load API",
        "version": "1.0.0",
        "endpoints": {
            "full_simulation": "/api/v1/heating-load/full-simulation",
            "steady_state": "/api/v1/heating-load/steady-state",
            "radiation": "/api/v1/heating-load/radiation",
            "transient": "/api/v1/heating-load/transient",
            "glasshouse": "/api/v1/heating-load/glasshouse",
            "climate": "/api/v1/climate/generate"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/v1/heating-load/full-simulation", response_model=FullSimulationResponse)
async def full_simulation(request: FullSimulationRequest):
    """
    Full heating load calculation with all physics models integrated.
    """
    try:
        logger.info(f"Full simulation request for lat={request.climate.latitude}, lon={request.climate.longitude}")
        
        # Generate climate data
        climate_data = generate_hourly_climate_data(
            request.climate.latitude,
            request.climate.longitude,
            request.climate.day_of_year
        )
        
        # Constants
        STEFAN_BOLTZMANN = 5.67e-8
        
        # Calculate results for each hour
        hourly_results = []
        
        for hour_data in climate_data:
            hour = hour_data['hour']
            outdoor_temp = hour_data['outdoor_temp']
            solar_radiation = hour_data['solar_radiation']
            sky_temp = hour_data['sky_temp']
            
            # Calculate losses and gains
            losses = calculate_total_building_loss(
                request.building.wall_area,
                request.building.wall_u_value,
                request.building.roof_area,
                request.building.roof_u_value,
                request.building.floor_area,
                request.building.floor_u_value,
                request.building.window_area,
                request.building.window_u_value,
                request.building.building_volume,
                request.building.ventilation_rate,
                request.building.indoor_temp,
                outdoor_temp
            )
            
            # Solar gain through windows
            solar_gain = request.building.window_area * request.building.shgc * solar_radiation
            
            # Longwave radiation to sky
            longwave_radiation = calculate_longwave_radiation_to_sky(
                request.building.window_area,
                request.building.emissivity,
                request.building.indoor_temp,
                sky_temp
            )
            
            # Radiation heat transfer (if enabled)
            radiation_heat_transfer = 0.0
            if request.simulation_options.include_radiation:
                # Simplified radiation calculation
                radiation_heat_transfer = (
                    request.building.emissivity * STEFAN_BOLTZMANN *
                    request.building.floor_area *
                    ((request.building.indoor_temp + 273.15)**4 - (outdoor_temp + 273.15)**4)
                )
            
            # Net heating load
            net_load = (
                losses['conductive_loss'] +
                losses['ventilation_loss'] -
                solar_gain +
                longwave_radiation
            )
            
            hourly_results.append(
                HourlyResult(
                    hour=hour,
                    outdoor_temp=outdoor_temp,
                    solar_radiation=solar_radiation,
                    conductive_loss=losses['conductive_loss'],
                    ventilation_loss=losses['ventilation_loss'],
                    solar_gain=solar_gain,
                    longwave_radiation=longwave_radiation,
                    radiation_heat_transfer=radiation_heat_transfer,
                    net_load=max(0, net_load),
                    indoor_temp_dynamic=request.building.indoor_temp
                )
            )
        
        # Calculate summary statistics
        hourly_loads = [r.net_load for r in hourly_results]
        total_heating_load_kwh = sum(hourly_loads) / 1000  # Convert Wh to kWh
        peak_load_w = max(hourly_loads)
        average_load_w = sum(hourly_loads) / len(hourly_loads)
        
        # Floor temperature (simplified)
        floor_temperature = request.building.indoor_temp - 1.5
        
        # Radiator output (simplified)
        radiator_output = average_load_w * 0.8
        
        summary = SimulationSummary(
            total_heating_load_kwh=total_heating_load_kwh,
            peak_load_w=peak_load_w,
            average_load_w=average_load_w,
            floor_temperature=floor_temperature,
            radiator_output=radiator_output
        )
        
        return FullSimulationResponse(
            hourly_results=hourly_results,
            summary=summary
        )
        
    except Exception as e:
        logger.error(f"Error in full simulation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/heating-load/steady-state", response_model=SteadyStateResponse)
async def steady_state_calculation(request: SteadyStateRequest):
    """
    Steady-state conduction calculation.
    """
    try:
        logger.info("Steady-state calculation request")
        
        # Generate climate data to get average outdoor temp
        climate_data = generate_hourly_climate_data(
            request.climate.latitude,
            request.climate.longitude,
            request.climate.day_of_year
        )
        avg_outdoor_temp = sum(d['outdoor_temp'] for d in climate_data) / len(climate_data)
        
        # Calculate losses
        losses = calculate_total_building_loss(
            request.building.wall_area,
            request.building.wall_u_value,
            request.building.roof_area,
            request.building.roof_u_value,
            request.building.floor_area,
            request.building.floor_u_value,
            request.building.window_area,
            request.building.window_u_value,
            request.building.building_volume,
            request.building.ventilation_rate,
            request.building.indoor_temp,
            avg_outdoor_temp
        )
        
        return SteadyStateResponse(
            conductive_loss=losses['conductive_loss'],
            wall_loss=losses['wall_loss'],
            roof_loss=losses['roof_loss'],
            floor_loss=losses['floor_loss'],
            window_loss=losses['window_loss'],
            ventilation_loss=losses['ventilation_loss'],
            total_loss=losses['total_loss']
        )
        
    except Exception as e:
        logger.error(f"Error in steady-state calculation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/heating-load/radiation", response_model=RadiationResponse)
async def radiation_calculation(request: RadiationRequest):
    """
    Radiation heat transfer calculation with view factors.
    """
    try:
        logger.info("Radiation calculation request")
        
        # Define surfaces
        surfaces = {
            'floor': {
                'area': request.building.floor_area,
                'emissivity': request.building.emissivity,
                'temperature': request.building.indoor_temp - 2
            },
            'ceiling': {
                'area': request.building.roof_area,
                'emissivity': request.building.emissivity,
                'temperature': request.building.indoor_temp + 1
            },
            'walls': {
                'area': request.building.wall_area,
                'emissivity': request.building.emissivity,
                'temperature': request.building.indoor_temp
            }
        }
        
        # Solve radiation exchange
        results = solve_radiation_exchange(surfaces, request.building.indoor_temp)
        
        # Calculate floor temperature
        floor_radiosity = results['floor']['radiosity']
        floor_temp = calculate_floor_temperature_from_radiosity(
            floor_radiosity,
            request.building.emissivity,
            5.0,  # Convective coefficient
            request.building.indoor_temp
        )
        
        # Calculate average radiative flux
        avg_flux = sum(r['net_flux'] for r in results.values()) / len(results)
        
        # View factors (simplified)
        view_factors = {
            'floor_to_ceiling': request.building.roof_area / (request.building.floor_area + request.building.roof_area),
            'floor_to_walls': request.building.wall_area / (request.building.floor_area + request.building.wall_area),
            'ceiling_to_floor': request.building.floor_area / (request.building.floor_area + request.building.roof_area)
        }
        
        # Radiosity values
        radiosity = {name: results[name]['radiosity'] for name in results}
        
        return RadiationResponse(
            radiative_flux=avg_flux,
            floor_temperature=floor_temp,
            view_factors=view_factors,
            radiosity=radiosity
        )
        
    except Exception as e:
        logger.error(f"Error in radiation calculation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/heating-load/transient", response_model=TransientResponse)
async def transient_calculation(request: TransientRequest):
    """
    Transient thermal simulation with RC model.
    """
    try:
        logger.info("Transient calculation request")
        
        # Generate climate data
        climate_data = generate_hourly_climate_data(
            request.climate.latitude,
            request.climate.longitude,
            request.climate.day_of_year
        )
        
        # Extract outdoor temps and solar gains
        outdoor_temps = [d['outdoor_temp'] for d in climate_data]
        solar_gains = [
            request.building.window_area * request.building.shgc * d['solar_radiation']
            for d in climate_data
        ]
        
        # Estimate thermal properties
        thermal_capacity = estimate_thermal_capacity(request.building.building_volume)
        thermal_resistance = estimate_thermal_resistance(
            request.building.wall_area,
            request.building.wall_u_value,
            request.building.roof_area,
            request.building.roof_u_value,
            request.building.floor_area,
            request.building.floor_u_value,
            request.building.window_area,
            request.building.window_u_value
        )
        
        # No active heating (free-floating)
        heating_inputs = [0.0] * len(outdoor_temps)
        
        # Simulate
        temps, loads = simulate_transient_response(
            request.building.indoor_temp,
            outdoor_temps,
            solar_gains,
            heating_inputs,
            thermal_resistance,
            thermal_capacity,
            request.simulation_options.timestep_seconds
        )
        
        # Calculate energy stored
        energy_stored = thermal_capacity * (temps[-1] - temps[0])
        
        return TransientResponse(
            hourly_temps=temps,
            hourly_loads=loads,
            final_temperature=temps[-1],
            energy_stored=energy_stored
        )
        
    except Exception as e:
        logger.error(f"Error in transient calculation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/heating-load/glasshouse", response_model=GlasshouseResponse)
async def glasshouse_calculation(request: GlasshouseRequest):
    """
    Specialized glasshouse/passive heating calculation.
    """
    try:
        logger.info("Glasshouse calculation request")
        
        # Generate climate data
        climate_data = generate_hourly_climate_data(
            request.climate.latitude,
            request.climate.longitude,
            request.climate.day_of_year
        )
        
        # Use peak solar hour (around noon)
        peak_hour_data = max(climate_data, key=lambda x: x['solar_radiation'])
        
        # Solve glasshouse temperatures
        T_interior, T_glass, T_collector, iterations = solve_glasshouse_temperatures(
            peak_hour_data['outdoor_temp'],
            peak_hour_data['solar_radiation'],
            request.building.window_area,
            request.building.floor_area * 0.8
        )
        
        # Calculate passive solar gain
        solar_absorbed = calculate_passive_solar_gain(
            request.building.window_area,
            0.85,  # Glass transmittance
            peak_hour_data['solar_radiation'],
            request.building.floor_area * 0.8,
            0.90  # Collector absorptance
        )
        
        # Calculate heating load
        U_back = 0.5
        heating_load = max(0, U_back * request.building.window_area * 
                          (request.building.indoor_temp - peak_hour_data['outdoor_temp']) - solar_absorbed)
        
        return GlasshouseResponse(
            interior_temp=T_interior,
            glass_temp=T_glass,
            collector_temp=T_collector,
            heating_load=heating_load,
            solar_absorbed=solar_absorbed,
            iterations=iterations
        )
        
    except Exception as e:
        logger.error(f"Error in glasshouse calculation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/climate/generate", response_model=ClimateResponse)
async def generate_climate(
    latitude: float,
    longitude: float,
    day_of_year: int = 15
):
    """
    Generate hourly climate data for given location.
    """
    try:
        logger.info(f"Climate generation request for lat={latitude}, lon={longitude}")
        
        # Generate climate data
        climate_data = generate_hourly_climate_data(latitude, longitude, day_of_year)
        
        # Convert to response model
        climate_list = [
            ClimateData(
                hour=d['hour'],
                outdoor_temp=d['outdoor_temp'],
                solar_radiation=d['solar_radiation'],
                sky_temp=d['sky_temp'],
                solar_elevation_deg=d['solar_elevation_deg']
            )
            for d in climate_data
        ]
        
        return ClimateResponse(
            climate_data=climate_list,
            latitude=latitude,
            longitude=longitude,
            day_of_year=day_of_year
        )
        
    except Exception as e:
        logger.error(f"Error generating climate data: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
