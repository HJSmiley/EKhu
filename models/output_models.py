"""Pydantic models for API responses."""

from pydantic import BaseModel, Field
from typing import List, Optional


class HourlyResult(BaseModel):
    """Hourly calculation results."""
    
    hour: int = Field(..., description="Hour of day (0-23)")
    outdoor_temp: float = Field(..., description="Outdoor temperature in °C")
    solar_radiation: float = Field(..., description="Solar radiation in W/m²")
    conductive_loss: float = Field(..., description="Conductive heat loss in W")
    ventilation_loss: float = Field(..., description="Ventilation heat loss in W")
    solar_gain: float = Field(..., description="Solar heat gain in W")
    longwave_radiation: float = Field(..., description="Longwave radiation in W")
    radiation_heat_transfer: Optional[float] = Field(None, description="Radiation heat transfer in W")
    net_load: float = Field(..., description="Net heating load in W")
    indoor_temp_dynamic: Optional[float] = Field(None, description="Dynamic indoor temperature in °C")


class SimulationSummary(BaseModel):
    """Summary statistics for simulation."""
    
    total_heating_load_kwh: float = Field(..., description="Total heating load in kWh")
    peak_load_w: float = Field(..., description="Peak load in W")
    average_load_w: float = Field(..., description="Average load in W")
    floor_temperature: Optional[float] = Field(None, description="Floor temperature in °C")
    radiator_output: Optional[float] = Field(None, description="Radiator output in W")


class FullSimulationResponse(BaseModel):
    """Response model for full heating load simulation."""
    
    hourly_results: List[HourlyResult]
    summary: SimulationSummary


class SteadyStateResponse(BaseModel):
    """Response model for steady-state conduction calculation."""
    
    conductive_loss: float = Field(..., description="Total conductive heat loss in W")
    wall_loss: float = Field(..., description="Wall heat loss in W")
    roof_loss: float = Field(..., description="Roof heat loss in W")
    floor_loss: float = Field(..., description="Floor heat loss in W")
    window_loss: float = Field(..., description="Window heat loss in W")
    ventilation_loss: float = Field(..., description="Ventilation heat loss in W")
    total_loss: float = Field(..., description="Total heat loss in W")


class RadiationResponse(BaseModel):
    """Response model for radiation heat transfer calculation."""
    
    radiative_flux: float = Field(..., description="Radiative heat flux in W/m²")
    floor_temperature: float = Field(..., description="Floor temperature in °C")
    view_factors: dict = Field(..., description="View factors dictionary")
    radiosity: dict = Field(..., description="Radiosity values")


class TransientResponse(BaseModel):
    """Response model for transient thermal simulation."""
    
    hourly_temps: List[float] = Field(..., description="Indoor temperatures over time")
    hourly_loads: List[float] = Field(..., description="Heating loads over time")
    final_temperature: float = Field(..., description="Final indoor temperature in °C")
    energy_stored: float = Field(..., description="Energy stored in thermal mass in J")


class GlasshouseResponse(BaseModel):
    """Response model for glasshouse/passive heating calculation."""
    
    interior_temp: float = Field(..., description="Interior temperature in °C")
    glass_temp: float = Field(..., description="Glass temperature in °C")
    collector_temp: float = Field(..., description="Collector temperature in °C")
    heating_load: float = Field(..., description="Net heating load in W")
    solar_absorbed: float = Field(..., description="Solar energy absorbed in W")
    iterations: int = Field(..., description="Number of iterations to converge")


class ClimateData(BaseModel):
    """Hourly climate data point."""
    
    hour: int = Field(..., description="Hour of day (0-23)")
    outdoor_temp: float = Field(..., description="Outdoor temperature in °C")
    solar_radiation: float = Field(..., description="Solar radiation in W/m²")
    sky_temp: float = Field(..., description="Sky temperature in °C")
    solar_elevation_deg: float = Field(..., description="Solar elevation angle in degrees")


class ClimateResponse(BaseModel):
    """Response model for climate data generation."""
    
    climate_data: List[ClimateData]
    latitude: float
    longitude: float
    day_of_year: int
