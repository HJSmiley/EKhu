"""Transient thermal analysis using RC thermal model."""

import numpy as np
from typing import List, Dict, Tuple


def rc_thermal_model_step(
    T_indoor: float,
    T_outdoor: float,
    thermal_resistance: float,
    thermal_capacity: float,
    heat_input: float,
    solar_gain: float,
    timestep: float
) -> float:
    """
    Calculate indoor temperature for next timestep using RC thermal model.
    
    RC model: C × dT/dt = (T_outdoor - T_indoor) / R + Φ + Q_solar
    
    Using forward Euler integration:
    T_i(t+Δt) = T_i(t) + (Δt/C) × [(T_e - T_i)/R + Φ + Q_solar]
    
    Args:
        T_indoor: Current indoor temperature in °C
        T_outdoor: Outdoor temperature in °C
        thermal_resistance: Thermal resistance in K/W
        thermal_capacity: Thermal capacity in J/K
        heat_input: Heating system input in W
        solar_gain: Solar heat gain in W
        timestep: Time step in seconds
    
    Returns:
        New indoor temperature in °C
    """
    # Heat flow through envelope
    Q_envelope = (T_outdoor - T_indoor) / thermal_resistance
    
    # Total heat input
    Q_total = Q_envelope + heat_input + solar_gain
    
    # Temperature change
    dT_dt = Q_total / thermal_capacity
    
    # New temperature
    T_new = T_indoor + dT_dt * timestep
    
    return T_new


def rc_thermal_model_implicit(
    T_indoor: float,
    T_outdoor: float,
    thermal_resistance: float,
    thermal_capacity: float,
    heat_input: float,
    solar_gain: float,
    timestep: float
) -> float:
    """
    Calculate indoor temperature using implicit (backward Euler) method.
    
    More stable than forward Euler for large timesteps.
    
    Args:
        T_indoor: Current indoor temperature in °C
        T_outdoor: Outdoor temperature in °C
        thermal_resistance: Thermal resistance in K/W
        thermal_capacity: Thermal capacity in J/K
        heat_input: Heating system input in W
        solar_gain: Solar heat gain in W
        timestep: Time step in seconds
    
    Returns:
        New indoor temperature in °C
    """
    # Coefficient for implicit scheme
    alpha = timestep / (thermal_capacity * thermal_resistance)
    
    # Solve: T_new = (T_old + alpha × (T_outdoor + R × (Φ + Q_solar))) / (1 + alpha)
    numerator = T_indoor + alpha * (T_outdoor + thermal_resistance * (heat_input + solar_gain))
    denominator = 1 + alpha
    
    T_new = numerator / denominator
    
    return T_new


def simulate_transient_response(
    initial_temp: float,
    outdoor_temps: List[float],
    solar_gains: List[float],
    heating_inputs: List[float],
    thermal_resistance: float,
    thermal_capacity: float,
    timestep: float,
    use_implicit: bool = True
) -> Tuple[List[float], List[float]]:
    """
    Simulate transient thermal response over multiple timesteps.
    
    Args:
        initial_temp: Initial indoor temperature in °C
        outdoor_temps: List of outdoor temperatures in °C
        solar_gains: List of solar heat gains in W
        heating_inputs: List of heating system inputs in W
        thermal_resistance: Thermal resistance in K/W
        thermal_capacity: Thermal capacity in J/K
        timestep: Time step in seconds
        use_implicit: Use implicit (True) or explicit (False) integration
    
    Returns:
        Tuple of (indoor temperatures, heating loads)
    """
    n_steps = len(outdoor_temps)
    indoor_temps = [initial_temp]
    heating_loads = []
    
    T_current = initial_temp
    
    for i in range(n_steps):
        T_outdoor = outdoor_temps[i]
        Q_solar = solar_gains[i]
        Q_heating = heating_inputs[i]
        
        # Calculate next temperature
        if use_implicit:
            T_next = rc_thermal_model_implicit(
                T_current, T_outdoor, thermal_resistance, thermal_capacity,
                Q_heating, Q_solar, timestep
            )
        else:
            T_next = rc_thermal_model_step(
                T_current, T_outdoor, thermal_resistance, thermal_capacity,
                Q_heating, Q_solar, timestep
            )
        
        # Calculate heating load needed
        Q_loss = (T_current - T_outdoor) / thermal_resistance
        Q_load = Q_loss - Q_solar
        
        indoor_temps.append(T_next)
        heating_loads.append(Q_load)
        
        T_current = T_next
    
    return indoor_temps, heating_loads


def calculate_thermal_time_constant(
    thermal_resistance: float,
    thermal_capacity: float
) -> float:
    """
    Calculate thermal time constant of the building.
    
    τ = R × C
    
    Args:
        thermal_resistance: Thermal resistance in K/W
        thermal_capacity: Thermal capacity in J/K
    
    Returns:
        Time constant in seconds
    """
    return thermal_resistance * thermal_capacity


def estimate_thermal_capacity(
    building_volume: float,
    wall_thickness: float = 0.3,
    density: float = 1800.0,
    specific_heat: float = 1000.0
) -> float:
    """
    Estimate building thermal capacity from volume and materials.
    
    Args:
        building_volume: Building volume in m³
        wall_thickness: Average wall thickness in m
        density: Material density in kg/m³
        specific_heat: Specific heat capacity in J/kg·K
    
    Returns:
        Thermal capacity in J/K
    """
    # Estimate mass of building envelope
    # Assume surface area is approximately 6 × volume^(2/3) for a cube
    surface_area = 6.0 * (building_volume ** (2.0 / 3.0))
    mass = surface_area * wall_thickness * density
    
    # Thermal capacity
    return mass * specific_heat


def estimate_thermal_resistance(
    wall_area: float,
    wall_u_value: float,
    roof_area: float,
    roof_u_value: float,
    floor_area: float,
    floor_u_value: float,
    window_area: float,
    window_u_value: float
) -> float:
    """
    Estimate overall thermal resistance from building elements.
    
    For parallel resistances: 1/R_total = Σ(A_i × U_i)
    
    Args:
        wall_area: Wall area in m²
        wall_u_value: Wall U-value in W/m²·K
        roof_area: Roof area in m²
        roof_u_value: Roof U-value in W/m²·K
        floor_area: Floor area in m²
        floor_u_value: Floor U-value in W/m²·K
        window_area: Window area in m²
        window_u_value: Window U-value in W/m²·K
    
    Returns:
        Overall thermal resistance in K/W
    """
    # Total conductance
    total_conductance = (
        wall_area * wall_u_value +
        roof_area * roof_u_value +
        floor_area * floor_u_value +
        window_area * window_u_value
    )
    
    # Overall resistance
    if total_conductance > 0:
        return 1.0 / total_conductance
    else:
        return float('inf')


def simulate_multiple_scenarios(
    scenarios: Dict[str, Dict],
    outdoor_temps: List[float],
    solar_gains: List[float],
    timestep: float
) -> Dict[str, Tuple[List[float], List[float]]]:
    """
    Simulate multiple scenarios for comparison.
    
    Args:
        scenarios: Dictionary of scenario parameters
        outdoor_temps: List of outdoor temperatures
        solar_gains: List of solar heat gains
        timestep: Time step in seconds
    
    Returns:
        Dictionary of results for each scenario
    """
    results = {}
    
    for name, params in scenarios.items():
        initial_temp = params['initial_temp']
        thermal_resistance = params['thermal_resistance']
        thermal_capacity = params['thermal_capacity']
        heating_inputs = params.get('heating_inputs', [0.0] * len(outdoor_temps))
        
        temps, loads = simulate_transient_response(
            initial_temp, outdoor_temps, solar_gains, heating_inputs,
            thermal_resistance, thermal_capacity, timestep
        )
        
        results[name] = (temps, loads)
    
    return results
