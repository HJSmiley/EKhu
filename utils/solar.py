"""Solar radiation and position calculations."""

import math
from typing import Tuple


def calculate_declination(day_of_year: int) -> float:
    """
    Calculate solar declination angle.
    
    Formula: δ = 23.45 × sin((360/365)(284 + n))
    
    Args:
        day_of_year: Day of year (1-365)
    
    Returns:
        Declination angle in degrees
    """
    return 23.45 * math.sin(math.radians((360 / 365) * (284 + day_of_year)))


def calculate_hour_angle(hour: int) -> float:
    """
    Calculate solar hour angle.
    
    Formula: H = (hour - 12) × 15°
    
    Args:
        hour: Hour of day (0-23)
    
    Returns:
        Hour angle in degrees
    """
    return (hour - 12) * 15


def calculate_solar_elevation(
    latitude: float,
    declination: float,
    hour_angle: float
) -> float:
    """
    Calculate solar elevation angle.
    
    Formula: sin(α) = sin(φ)sin(δ) + cos(φ)cos(δ)cos(H)
    
    Args:
        latitude: Latitude in degrees
        declination: Declination angle in degrees
        hour_angle: Hour angle in degrees
    
    Returns:
        Solar elevation angle in radians (0 if below horizon)
    """
    lat_rad = math.radians(latitude)
    decl_rad = math.radians(declination)
    hour_rad = math.radians(hour_angle)
    
    sin_elev = (
        math.sin(lat_rad) * math.sin(decl_rad) +
        math.cos(lat_rad) * math.cos(decl_rad) * math.cos(hour_rad)
    )
    
    # Clamp to valid range and return 0 if below horizon
    sin_elev = max(-1.0, min(1.0, sin_elev))
    elevation = math.asin(sin_elev)
    
    return max(0.0, elevation)


def calculate_solar_azimuth(
    latitude: float,
    declination: float,
    hour_angle: float,
    elevation: float
) -> float:
    """
    Calculate solar azimuth angle.
    
    Args:
        latitude: Latitude in degrees
        declination: Declination angle in degrees
        hour_angle: Hour angle in degrees
        elevation: Solar elevation in radians
    
    Returns:
        Solar azimuth angle in radians (from north)
    """
    lat_rad = math.radians(latitude)
    decl_rad = math.radians(declination)
    hour_rad = math.radians(hour_angle)
    
    if elevation <= 0:
        return 0.0
    
    cos_azimuth = (
        math.sin(decl_rad) - math.sin(lat_rad) * math.sin(elevation)
    ) / (math.cos(lat_rad) * math.cos(elevation))
    
    # Clamp to valid range
    cos_azimuth = max(-1.0, min(1.0, cos_azimuth))
    azimuth = math.acos(cos_azimuth)
    
    # Adjust for afternoon (hour angle > 0)
    if hour_angle > 0:
        azimuth = 2 * math.pi - azimuth
    
    return azimuth


def calculate_solar_radiation(
    solar_elevation: float,
    solar_constant: float = 1367.0,
    atmospheric_transmittance: float = 0.7
) -> Tuple[float, float]:
    """
    Calculate direct normal irradiance (DNI) and global horizontal irradiance (GHI).
    
    Args:
        solar_elevation: Solar elevation angle in radians
        solar_constant: Solar constant in W/m²
        atmospheric_transmittance: Atmospheric transmittance factor
    
    Returns:
        Tuple of (DNI, GHI) in W/m²
    """
    if solar_elevation <= 0:
        return 0.0, 0.0
    
    # Air mass calculation
    air_mass = 1.0 / math.sin(solar_elevation)
    
    # Atmospheric transmittance model
    transmittance = atmospheric_transmittance ** (air_mass ** 0.678)
    
    # Direct Normal Irradiance
    DNI = solar_constant * transmittance
    
    # Global Horizontal Irradiance
    GHI = DNI * math.sin(solar_elevation)
    
    return DNI, max(0.0, GHI)


def calculate_incidence_angle(
    solar_elevation: float,
    solar_azimuth: float,
    surface_tilt: float,
    surface_azimuth: float
) -> float:
    """
    Calculate angle of incidence between sun and surface.
    
    Args:
        solar_elevation: Solar elevation in radians
        solar_azimuth: Solar azimuth in radians
        surface_tilt: Surface tilt from horizontal in radians
        surface_azimuth: Surface azimuth in radians
    
    Returns:
        Incidence angle in radians
    """
    cos_incident = (
        math.sin(solar_elevation) * math.cos(surface_tilt) +
        math.cos(solar_elevation) * math.sin(surface_tilt) *
        math.cos(solar_azimuth - surface_azimuth)
    )
    
    cos_incident = max(-1.0, min(1.0, cos_incident))
    return math.acos(cos_incident)


def calculate_irradiance_on_surface(
    DNI: float,
    GHI: float,
    incidence_angle: float,
    diffuse_fraction: float = 0.3
) -> float:
    """
    Calculate total irradiance on a tilted surface.
    
    Args:
        DNI: Direct normal irradiance in W/m²
        GHI: Global horizontal irradiance in W/m²
        incidence_angle: Incidence angle in radians
        diffuse_fraction: Fraction of radiation that is diffuse
    
    Returns:
        Total irradiance on surface in W/m²
    """
    # Direct component
    direct = DNI * math.cos(incidence_angle) if incidence_angle < math.pi / 2 else 0.0
    
    # Diffuse component (isotropic sky model)
    diffuse = GHI * diffuse_fraction
    
    return direct + diffuse


def calculate_sky_temperature(
    outdoor_temp: float,
    cloud_cover: float = 0.0,
    relative_humidity: float = 0.5
) -> float:
    """
    Calculate effective sky temperature for longwave radiation.
    
    Args:
        outdoor_temp: Outdoor air temperature in °C
        cloud_cover: Cloud cover fraction (0-1)
        relative_humidity: Relative humidity (0-1)
    
    Returns:
        Sky temperature in °C
    """
    # Simple model: sky temperature is lower than air temperature
    # Clear sky depression depends on humidity
    clear_sky_depression = 6.0 * (1.0 - relative_humidity * 0.5)
    
    # Cloud cover reduces depression
    effective_depression = clear_sky_depression * (1.0 - cloud_cover * 0.8)
    
    return outdoor_temp - effective_depression
