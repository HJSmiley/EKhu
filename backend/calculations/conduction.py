"""Steady-state conduction heat transfer calculations."""

import numpy as np
from typing import Dict, Tuple
from utils.matrix_solver import solve_linear_system, build_thermal_network_matrix


# Physical constants
AIR_DENSITY = 1.2  # kg/m³
SPECIFIC_HEAT_AIR = 1005  # J/kg·K


def calculate_thermal_resistance(
    thickness: float,
    thermal_conductivity: float,
    internal_resistance: float = 0.13,
    external_resistance: float = 0.04
) -> float:
    """
    Calculate total thermal resistance of a wall assembly.
    
    Formula: Rt = Ri + e/λ + Re
    
    Args:
        thickness: Material thickness in m
        thermal_conductivity: Thermal conductivity in W/m·K
        internal_resistance: Internal surface resistance in m²·K/W
        external_resistance: External surface resistance in m²·K/W
    
    Returns:
        Total thermal resistance in m²·K/W
    """
    material_resistance = thickness / thermal_conductivity
    return internal_resistance + material_resistance + external_resistance


def calculate_u_value(thermal_resistance: float) -> float:
    """
    Calculate U-value from thermal resistance.
    
    Args:
        thermal_resistance: Total thermal resistance in m²·K/W
    
    Returns:
        U-value in W/m²·K
    """
    return 1.0 / thermal_resistance


def calculate_conductive_loss(
    area: float,
    u_value: float,
    indoor_temp: float,
    outdoor_temp: float
) -> float:
    """
    Calculate conductive heat loss through a building element.
    
    Formula: Q = A × U × ΔT
    
    Args:
        area: Surface area in m²
        u_value: U-value in W/m²·K
        indoor_temp: Indoor temperature in °C
        outdoor_temp: Outdoor temperature in °C
    
    Returns:
        Heat loss in W
    """
    delta_t = indoor_temp - outdoor_temp
    return area * u_value * delta_t


def calculate_ventilation_loss(
    building_volume: float,
    ventilation_rate: float,
    indoor_temp: float,
    outdoor_temp: float
) -> float:
    """
    Calculate ventilation heat loss.
    
    Formula: Q = ṁ × cp × ΔT
    where ṁ = ρ × V × ACH / 3600
    
    Args:
        building_volume: Building volume in m³
        ventilation_rate: Air changes per hour (ACH)
        indoor_temp: Indoor temperature in °C
        outdoor_temp: Outdoor temperature in °C
    
    Returns:
        Ventilation heat loss in W
    """
    mass_flow = (AIR_DENSITY * building_volume * ventilation_rate) / 3600
    delta_t = indoor_temp - outdoor_temp
    return mass_flow * SPECIFIC_HEAT_AIR * delta_t


def calculate_total_building_loss(
    wall_area: float,
    wall_u_value: float,
    roof_area: float,
    roof_u_value: float,
    floor_area: float,
    floor_u_value: float,
    window_area: float,
    window_u_value: float,
    building_volume: float,
    ventilation_rate: float,
    indoor_temp: float,
    outdoor_temp: float
) -> Dict[str, float]:
    """
    Calculate total heat loss for a building.
    
    Args:
        wall_area: Wall area in m²
        wall_u_value: Wall U-value in W/m²·K
        roof_area: Roof area in m²
        roof_u_value: Roof U-value in W/m²·K
        floor_area: Floor area in m²
        floor_u_value: Floor U-value in W/m²·K
        window_area: Window area in m²
        window_u_value: Window U-value in W/m²·K
        building_volume: Building volume in m³
        ventilation_rate: Ventilation rate (ACH)
        indoor_temp: Indoor temperature in °C
        outdoor_temp: Outdoor temperature in °C
    
    Returns:
        Dictionary with component and total losses
    """
    wall_loss = calculate_conductive_loss(wall_area, wall_u_value, indoor_temp, outdoor_temp)
    roof_loss = calculate_conductive_loss(roof_area, roof_u_value, indoor_temp, outdoor_temp)
    floor_loss = calculate_conductive_loss(floor_area, floor_u_value, indoor_temp, outdoor_temp)
    window_loss = calculate_conductive_loss(window_area, window_u_value, indoor_temp, outdoor_temp)
    
    conductive_loss = wall_loss + roof_loss + floor_loss + window_loss
    ventilation_loss = calculate_ventilation_loss(
        building_volume, ventilation_rate, indoor_temp, outdoor_temp
    )
    
    total_loss = conductive_loss + ventilation_loss
    
    return {
        'wall_loss': wall_loss,
        'roof_loss': roof_loss,
        'floor_loss': floor_loss,
        'window_loss': window_loss,
        'conductive_loss': conductive_loss,
        'ventilation_loss': ventilation_loss,
        'total_loss': total_loss
    }


def solve_multi_zone_temperatures(
    zones: list,
    conductances: Dict[Tuple[str, str], float],
    boundary_temps: Dict[str, float],
    heat_sources: Dict[str, float]
) -> Dict[str, float]:
    """
    Solve multi-zone heat transfer problem using matrix methods.
    
    This implements the Ax = b formulation where:
    - A is the conductance matrix
    - x is the unknown temperature vector
    - b is the heat source vector (including boundary conditions)
    
    Args:
        zones: List of zone names
        conductances: Thermal conductances between zones (W/K)
        boundary_temps: Known boundary temperatures (°C)
        heat_sources: Heat sources in each zone (W)
    
    Returns:
        Dictionary of zone temperatures
    """
    # Build thermal network matrix
    K, Q = build_thermal_network_matrix(zones, conductances, boundary_temps)
    
    # Add internal heat sources
    for i, zone in enumerate(zones):
        if zone in heat_sources:
            Q[i] += heat_sources[zone]
    
    # Solve system
    temperatures = solve_linear_system(K, Q)
    
    return {zone: float(temperatures[i]) for i, zone in enumerate(zones)}
