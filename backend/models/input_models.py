"""Pydantic models for input validation."""

from pydantic import BaseModel, Field
from typing import Optional


class BuildingParams(BaseModel):
    """Building envelope and system parameters."""
    
    wall_area: float = Field(..., gt=0, description="Wall area in m²")
    wall_u_value: float = Field(..., gt=0, description="Wall U-value in W/m²·K")
    roof_area: float = Field(..., gt=0, description="Roof area in m²")
    roof_u_value: float = Field(..., gt=0, description="Roof U-value in W/m²·K")
    floor_area: float = Field(..., gt=0, description="Floor area in m²")
    floor_u_value: float = Field(..., gt=0, description="Floor U-value in W/m²·K")
    window_area: float = Field(..., gt=0, description="Window area in m²")
    window_u_value: float = Field(..., gt=0, description="Window U-value in W/m²·K")
    shgc: float = Field(..., ge=0, le=1, description="Solar heat gain coefficient")
    ventilation_rate: float = Field(..., gt=0, description="Ventilation rate (ACH)")
    building_volume: float = Field(..., gt=0, description="Building volume in m³")
    indoor_temp: float = Field(..., description="Indoor temperature in °C")
    
    # Optional parameters for advanced calculations
    emissivity: Optional[float] = Field(0.85, ge=0, le=1, description="Surface emissivity")
    reflectivity: Optional[float] = Field(0.15, ge=0, le=1, description="Surface reflectivity")
    thermal_capacity: Optional[float] = Field(1e7, gt=0, description="Thermal capacity in J/K")
    thermal_resistance: Optional[float] = Field(8e-3, gt=0, description="Thermal resistance in K/W")


class ClimateParams(BaseModel):
    """Climate location and time parameters."""
    
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    day_of_year: int = Field(15, ge=1, le=365, description="Day of year (1-365)")


class SimulationOptions(BaseModel):
    """Simulation configuration options."""
    
    include_radiation: bool = Field(True, description="Include radiation heat transfer")
    include_transient: bool = Field(True, description="Include transient effects")
    timestep_seconds: int = Field(3600, gt=0, description="Simulation timestep in seconds")


class FullSimulationRequest(BaseModel):
    """Request model for full heating load simulation."""
    
    building: BuildingParams
    climate: ClimateParams
    simulation_options: Optional[SimulationOptions] = SimulationOptions()


class SteadyStateRequest(BaseModel):
    """Request model for steady-state conduction calculation."""
    
    building: BuildingParams
    climate: ClimateParams


class RadiationRequest(BaseModel):
    """Request model for radiation heat transfer calculation."""
    
    building: BuildingParams
    climate: ClimateParams


class TransientRequest(BaseModel):
    """Request model for transient thermal simulation."""
    
    building: BuildingParams
    climate: ClimateParams
    simulation_options: Optional[SimulationOptions] = SimulationOptions()


class GlasshouseRequest(BaseModel):
    """Request model for glasshouse/passive heating calculation."""
    
    building: BuildingParams
    climate: ClimateParams


class ClimateRequest(BaseModel):
    """Request model for climate data generation."""
    
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    day_of_year: int = Field(15, ge=1, le=365, description="Day of year (1-365)")
