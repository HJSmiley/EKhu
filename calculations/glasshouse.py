"""Glasshouse and passive solar heating calculations."""

import numpy as np
from typing import Tuple, Dict


# Physical constants
STEFAN_BOLTZMANN = 5.67e-8  # W/m²·K⁴


def calculate_radiative_coefficient(
    emissivity: float,
    temp1: float,
    temp2: float
) -> float:
    """
    Calculate linearized radiative heat transfer coefficient.
    
    hr = ε × σ × (T₁² + T₂²) × (T₁ + T₂)
    
    Args:
        emissivity: Surface emissivity
        temp1: Temperature 1 in K
        temp2: Temperature 2 in K
    
    Returns:
        Radiative coefficient in W/m²·K
    """
    return emissivity * STEFAN_BOLTZMANN * (temp1**2 + temp2**2) * (temp1 + temp2)


def solve_glasshouse_temperatures(
    T_outdoor: float,
    solar_irradiance: float,
    glass_area: float,
    collector_area: float,
    glass_transmittance: float = 0.85,
    glass_absorptance: float = 0.05,
    collector_absorptance: float = 0.90,
    emissivity_glass: float = 0.90,
    emissivity_collector: float = 0.85,
    emissivity_interior: float = 0.90,
    h_conv_ext: float = 15.0,
    h_conv_int: float = 5.0,
    U_back: float = 0.5,
    max_iterations: int = 100,
    tolerance: float = 0.01
) -> Tuple[float, float, float, int]:
    """
    Solve glasshouse energy balance using iterative matrix solution.
    
    Energy balance equations:
    1. Interior: convection from glass + radiation from collector = back loss
    2. Glass: solar absorption + radiation exchange = convection to outside and inside
    3. Collector: solar absorption = radiation to glass + convection to interior
    
    Args:
        T_outdoor: Outdoor temperature in °C
        solar_irradiance: Solar irradiance in W/m²
        glass_area: Glass area in m²
        collector_area: Collector area in m²
        glass_transmittance: Glass solar transmittance
        glass_absorptance: Glass solar absorptance
        collector_absorptance: Collector solar absorptance
        emissivity_glass: Glass emissivity
        emissivity_collector: Collector emissivity
        emissivity_interior: Interior surface emissivity
        h_conv_ext: External convection coefficient in W/m²·K
        h_conv_int: Internal convection coefficient in W/m²·K
        U_back: Back wall U-value in W/m²·K
        max_iterations: Maximum iterations for convergence
        tolerance: Temperature tolerance for convergence in K
    
    Returns:
        Tuple of (interior temp, glass temp, collector temp, iterations)
    """
    # Initial guess (in Kelvin)
    T_i = T_outdoor + 10 + 273.15  # Interior
    T_g = T_outdoor + 5 + 273.15   # Glass
    T_c = T_outdoor + 15 + 273.15  # Collector
    T_e = T_outdoor + 273.15       # Outdoor
    
    # Solar heat inputs
    Q_glass_solar = glass_absorptance * solar_irradiance * glass_area
    Q_collector_solar = collector_absorptance * glass_transmittance * solar_irradiance * collector_area
    
    for iteration in range(max_iterations):
        # Calculate radiative heat transfer coefficients
        hr_gc = calculate_radiative_coefficient(
            emissivity_glass * emissivity_collector, T_g, T_c
        )
        hr_gi = calculate_radiative_coefficient(
            emissivity_glass * emissivity_interior, T_g, T_i
        )
        hr_ci = calculate_radiative_coefficient(
            emissivity_collector * emissivity_interior, T_c, T_i
        )
        
        # Build coefficient matrix [A] and constant vector [b]
        # For system: [A] × [T_i, T_g, T_c]ᵀ = [b]
        
        # Equation 1: Interior energy balance
        # h_conv_int × (T_g - T_i) + hr_ci × (T_c - T_i) = U_back × (T_i - T_e)
        a11 = h_conv_int + hr_ci + U_back
        a12 = -h_conv_int
        a13 = -hr_ci
        b1 = U_back * T_e
        
        # Equation 2: Glass energy balance
        # Q_glass_solar + h_conv_ext × (T_e - T_g) + hr_gi × (T_i - T_g) + hr_gc × (T_c - T_g) = 0
        a21 = -hr_gi
        a22 = h_conv_ext + hr_gi + hr_gc
        a23 = -hr_gc
        b2 = Q_glass_solar + h_conv_ext * T_e
        
        # Equation 3: Collector energy balance
        # Q_collector_solar = hr_gc × (T_c - T_g) + hr_ci × (T_c - T_i)
        a31 = -hr_ci
        a32 = -hr_gc
        a33 = hr_gc + hr_ci
        b3 = Q_collector_solar
        
        # Solve system
        A = np.array([
            [a11, a12, a13],
            [a21, a22, a23],
            [a31, a32, a33]
        ])
        b = np.array([b1, b2, b3])
        
        try:
            T_new = np.linalg.solve(A, b)
        except np.linalg.LinAlgError:
            # If matrix is singular, use previous values
            break
        
        T_i_new, T_g_new, T_c_new = T_new
        
        # Check convergence
        max_change = max(
            abs(T_i_new - T_i),
            abs(T_g_new - T_g),
            abs(T_c_new - T_c)
        )
        
        if max_change < tolerance:
            T_i, T_g, T_c = T_i_new, T_g_new, T_c_new
            break
        
        # Update temperatures with relaxation
        relax = 0.5  # Relaxation factor for stability
        T_i = T_i + relax * (T_i_new - T_i)
        T_g = T_g + relax * (T_g_new - T_g)
        T_c = T_c + relax * (T_c_new - T_c)
    
    # Convert back to Celsius
    return (T_i - 273.15, T_g - 273.15, T_c - 273.15, iteration + 1)


def calculate_glasshouse_heating_load(
    T_interior: float,
    T_outdoor: float,
    T_setpoint: float,
    glass_area: float,
    U_back: float
) -> float:
    """
    Calculate heating load needed for glasshouse.
    
    Args:
        T_interior: Interior temperature in °C
        T_outdoor: Outdoor temperature in °C
        T_setpoint: Desired setpoint temperature in °C
        glass_area: Glass area in m²
        U_back: Back wall U-value in W/m²·K
    
    Returns:
        Heating load in W (0 if passive heating is sufficient)
    """
    # Heat loss through back
    Q_loss = U_back * glass_area * (T_interior - T_outdoor)
    
    # If interior temp is below setpoint, heating is needed
    if T_interior < T_setpoint:
        # Additional heating needed
        return Q_loss + U_back * glass_area * (T_setpoint - T_interior)
    else:
        # Passive heating is sufficient
        return 0.0


def calculate_passive_solar_gain(
    glass_area: float,
    glass_transmittance: float,
    solar_irradiance: float,
    collector_area: float,
    collector_absorptance: float
) -> float:
    """
    Calculate total passive solar gain through glasshouse.
    
    Args:
        glass_area: Glass area in m²
        glass_transmittance: Glass solar transmittance
        solar_irradiance: Solar irradiance in W/m²
        collector_area: Collector area in m²
        collector_absorptance: Collector solar absorptance
    
    Returns:
        Total solar gain in W
    """
    # Direct transmission through glass
    Q_direct = glass_transmittance * solar_irradiance * glass_area
    
    # Absorption by collector
    Q_collector = collector_absorptance * glass_transmittance * solar_irradiance * collector_area
    
    return Q_direct + Q_collector


def optimize_glasshouse_design(
    T_outdoor: float,
    solar_irradiance: float,
    building_load: float,
    glass_area_range: Tuple[float, float] = (10.0, 100.0),
    steps: int = 20
) -> Dict[str, float]:
    """
    Optimize glasshouse design to meet building heating load.
    
    Args:
        T_outdoor: Outdoor temperature in °C
        solar_irradiance: Solar irradiance in W/m²
        building_load: Building heating load in W
        glass_area_range: Range of glass areas to test (min, max)
        steps: Number of steps to test
    
    Returns:
        Dictionary with optimal design parameters
    """
    best_result = None
    min_area = glass_area_range[0]
    max_area = glass_area_range[1]
    step_size = (max_area - min_area) / steps
    
    for i in range(steps + 1):
        glass_area = min_area + i * step_size
        collector_area = glass_area * 0.8  # 80% of glass area
        
        # Solve for temperatures
        T_i, T_g, T_c, iters = solve_glasshouse_temperatures(
            T_outdoor, solar_irradiance, glass_area, collector_area
        )
        
        # Calculate passive gain
        passive_gain = calculate_passive_solar_gain(
            glass_area, 0.85, solar_irradiance, collector_area, 0.90
        )
        
        # Check if it meets the load
        if passive_gain >= building_load * 0.9:  # 90% threshold
            if best_result is None or glass_area < best_result['glass_area']:
                best_result = {
                    'glass_area': glass_area,
                    'collector_area': collector_area,
                    'interior_temp': T_i,
                    'passive_gain': passive_gain,
                    'efficiency': passive_gain / building_load if building_load > 0 else 0
                }
    
    return best_result if best_result else {
        'glass_area': max_area,
        'collector_area': max_area * 0.8,
        'interior_temp': 0.0,
        'passive_gain': 0.0,
        'efficiency': 0.0
    }
