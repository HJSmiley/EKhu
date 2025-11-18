"""Climate data generation module."""

import math
from typing import List, Dict
from utils.solar import (
    calculate_declination,
    calculate_hour_angle,
    calculate_solar_elevation,
    calculate_solar_radiation,
    calculate_sky_temperature
)


def generate_outdoor_temperature(
    hour: int,
    latitude: float,
    day_of_year: int = 15
) -> float:
    """
    Generate synthetic outdoor temperature based on location and time.
    
    Args:
        hour: Hour of day (0-23)
        latitude: Latitude in degrees
        day_of_year: Day of year (1-365)
    
    Returns:
        Outdoor temperature in °C
    """
    # Base temperature depends on latitude
    # Reference: Seoul at 37°N has winter temp around -5°C
    base_temp = -5.0 - abs(latitude - 37.0) * 0.7
    
    # Daily amplitude (diurnal variation)
    daily_amplitude = 6.0
    
    # Temperature peaks around 14:00 (hour 14)
    temp = base_temp + daily_amplitude * math.sin(
        ((hour - 8) / 24) * 2 * math.pi
    )
    
    return temp


def generate_hourly_climate_data(
    latitude: float,
    longitude: float,
    day_of_year: int = 15
) -> List[Dict]:
    """
    Generate 24 hours of climate data for a given location.
    
    Args:
        latitude: Latitude in degrees
        longitude: Longitude in degrees
        day_of_year: Day of year (1-365, default 15 for mid-January)
    
    Returns:
        List of hourly climate data dictionaries
    """
    declination = calculate_declination(day_of_year)
    climate_data = []
    
    for hour in range(24):
        # Solar position
        hour_angle = calculate_hour_angle(hour)
        solar_elevation = calculate_solar_elevation(latitude, declination, hour_angle)
        
        # Solar radiation
        DNI, GHI = calculate_solar_radiation(solar_elevation)
        
        # Outdoor temperature
        outdoor_temp = generate_outdoor_temperature(hour, latitude, day_of_year)
        
        # Sky temperature for longwave radiation
        sky_temp = calculate_sky_temperature(outdoor_temp)
        
        climate_data.append({
            'hour': hour,
            'outdoor_temp': outdoor_temp,
            'solar_radiation': GHI,
            'sky_temp': sky_temp,
            'solar_elevation_deg': math.degrees(solar_elevation),
            'declination': declination,
            'hour_angle': hour_angle
        })
    
    return climate_data


def interpolate_climate_data(
    climate_data: List[Dict],
    timestep_seconds: int = 3600
) -> List[Dict]:
    """
    Interpolate climate data to finer timesteps.
    
    Args:
        climate_data: Hourly climate data
        timestep_seconds: Desired timestep in seconds
    
    Returns:
        Interpolated climate data
    """
    if timestep_seconds >= 3600:
        return climate_data
    
    steps_per_hour = 3600 // timestep_seconds
    interpolated = []
    
    for i in range(len(climate_data)):
        current = climate_data[i]
        next_hour = climate_data[(i + 1) % len(climate_data)]
        
        for step in range(steps_per_hour):
            fraction = step / steps_per_hour
            
            interpolated.append({
                'hour': current['hour'] + step / steps_per_hour,
                'outdoor_temp': current['outdoor_temp'] + 
                    fraction * (next_hour['outdoor_temp'] - current['outdoor_temp']),
                'solar_radiation': current['solar_radiation'] + 
                    fraction * (next_hour['solar_radiation'] - current['solar_radiation']),
                'sky_temp': current['sky_temp'] + 
                    fraction * (next_hour['sky_temp'] - current['sky_temp']),
                'solar_elevation_deg': current['solar_elevation_deg']
            })
    
    return interpolated
