"""Radiation heat transfer calculations with view factors."""

import math
from typing import Dict, Tuple
from utils.matrix_solver import calculate_view_factors, solve_radiosity_system


# Physical constants
STEFAN_BOLTZMANN = 5.67e-8  # W/m²·K⁴


def calculate_radiative_heat_transfer(
    area: float,
    emissivity: float,
    temp_surface: float,
    temp_environment: float
) -> float:
    """
    Calculate radiative heat transfer using Stefan-Boltzmann law.
    
    Formula: Q = ε × σ × A × (T₁⁴ - T₂⁴)
    
    Args:
        area: Surface area in m²
        emissivity: Surface emissivity (0-1)
        temp_surface: Surface temperature in °C
        temp_environment: Environment temperature in °C
    
    Returns:
        Radiative heat transfer in W
    """
    T1_K = temp_surface + 273.15
    T2_K = temp_environment + 273.15
    
    return emissivity * STEFAN_BOLTZMANN * area * (T1_K**4 - T2_K**4)


def calculate_radiation_coefficient(
    emissivity: float,
    temp_surface: float,
    temp_environment: float
) -> float:
    """
    Calculate linearized radiation heat transfer coefficient.
    
    Formula: hr = 4 × ε × σ × Tm³
    where Tm = (T₁ + T₂) / 2
    
    Args:
        emissivity: Surface emissivity (0-1)
        temp_surface: Surface temperature in °C
        temp_environment: Environment temperature in °C
    
    Returns:
        Radiation coefficient in W/m²·K
    """
    T1_K = temp_surface + 273.15
    T2_K = temp_environment + 273.15
    Tm = (T1_K + T2_K) / 2
    
    return 4 * emissivity * STEFAN_BOLTZMANN * (Tm ** 3)


def calculate_view_factor_parallel_surfaces(
    area1: float,
    area2: float,
    distance: float
) -> Tuple[float, float]:
    """
    Calculate view factors between parallel rectangular surfaces.
    
    Args:
        area1: Area of surface 1 in m²
        area2: Area of surface 2 in m²
        distance: Distance between surfaces in m
    
    Returns:
        Tuple of (F12, F21) view factors
    """
    # Simplified model for parallel surfaces
    # For more accurate calculations, would use Hottel's crossed-string method
    
    # Approximate for large parallel surfaces
    if area1 > 0 and area2 > 0:
        # Shape factor based on area ratio and distance
        F12 = min(1.0, area2 / (area1 + area2))
        F21 = F12 * area1 / area2
    else:
        F12 = 0.0
        F21 = 0.0
    
    return F12, F21


def solve_radiation_exchange(
    surfaces: Dict[str, Dict],
    ambient_temp: float = 20.0
) -> Dict[str, float]:
    """
    Solve radiation exchange between multiple surfaces.
    
    Uses the radiosity method to account for multiple reflections.
    
    Args:
        surfaces: Dictionary of surface properties
                  Each surface has: area, emissivity, temperature
        ambient_temp: Ambient temperature in °C
    
    Returns:
        Dictionary with radiosity and net heat flux for each surface
    """
    # Extract surface properties
    surface_names = list(surfaces.keys())
    areas = {name: props['area'] for name, props in surfaces.items()}
    emissivities = {name: props['emissivity'] for name, props in surfaces.items()}
    
    # Convert temperatures to Kelvin
    temperatures = {
        name: props.get('temperature', ambient_temp) + 273.15
        for name, props in surfaces.items()
    }
    
    # Calculate view factors
    view_factors = calculate_view_factors(areas)
    
    # Solve radiosity system
    radiosities = solve_radiosity_system(
        view_factors, emissivities, temperatures, STEFAN_BOLTZMANN
    )
    
    # Calculate net radiative flux for each surface
    results = {}
    for name in surface_names:
        eps = emissivities[name]
        T = temperatures[name]
        J = radiosities[name]
        
        # Net radiative flux: q = (E - J) / ((1 - ε) / ε)
        E = eps * STEFAN_BOLTZMANN * (T ** 4)
        q = (E - J) * eps / (1 - eps) if eps < 1.0 else 0.0
        
        results[name] = {
            'radiosity': J,
            'net_flux': q,
            'emissive_power': E
        }
    
    return results


def calculate_floor_temperature_from_radiosity(
    radiosity: float,
    emissivity: float,
    convective_coeff: float,
    air_temp: float,
    radiative_sources: float = 0.0
) -> float:
    """
    Calculate floor temperature from radiosity balance.
    
    Energy balance: radiative exchange + convection + internal sources = 0
    
    Args:
        radiosity: Floor radiosity in W/m²
        emissivity: Floor emissivity
        convective_coeff: Convective heat transfer coefficient in W/m²·K
        air_temp: Air temperature in °C
        radiative_sources: Additional radiative sources in W/m²
    
    Returns:
        Floor temperature in °C
    """
    # Iterative solution for floor temperature
    T_floor = air_temp  # Initial guess
    
    for _ in range(50):  # Maximum iterations
        T_floor_K = T_floor + 273.15
        
        # Emissive power
        E = emissivity * STEFAN_BOLTZMANN * (T_floor_K ** 4)
        
        # Net radiative flux
        q_rad = (E - radiosity) * emissivity / (1 - emissivity) if emissivity < 1.0 else 0.0
        
        # Convective flux
        q_conv = convective_coeff * (T_floor - air_temp)
        
        # Energy balance
        residual = q_rad + q_conv - radiative_sources
        
        # Check convergence
        if abs(residual) < 0.1:
            break
        
        # Update temperature (simple relaxation)
        T_floor -= residual / (4 * emissivity * STEFAN_BOLTZMANN * (T_floor_K ** 3) + convective_coeff)
    
    return T_floor


def calculate_longwave_radiation_to_sky(
    window_area: float,
    emissivity: float,
    indoor_temp: float,
    sky_temp: float
) -> float:
    """
    Calculate longwave radiation heat loss to sky through windows.
    
    Args:
        window_area: Window area in m²
        emissivity: Effective emissivity
        indoor_temp: Indoor temperature in °C
        sky_temp: Sky temperature in °C
    
    Returns:
        Longwave radiation loss in W
    """
    return calculate_radiative_heat_transfer(
        window_area, emissivity, indoor_temp, sky_temp
    )


def calculate_solar_radiation_absorbed(
    area: float,
    absorptivity: float,
    solar_irradiance: float,
    incidence_angle: float = 0.0
) -> float:
    """
    Calculate solar radiation absorbed by a surface.
    
    Args:
        area: Surface area in m²
        absorptivity: Solar absorptivity (0-1)
        solar_irradiance: Solar irradiance in W/m²
        incidence_angle: Angle of incidence in radians
    
    Returns:
        Absorbed solar radiation in W
    """
    # Effective irradiance accounting for incidence angle
    effective_irradiance = solar_irradiance * math.cos(incidence_angle)
    
    return area * absorptivity * max(0.0, effective_irradiance)
