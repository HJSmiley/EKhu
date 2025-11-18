"""Matrix solver utilities using NumPy."""

import numpy as np
from typing import List, Dict, Tuple


def solve_linear_system(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Solve a linear system Ax = b using NumPy's linear algebra solver.
    
    Args:
        A: Coefficient matrix (n x n)
        b: Right-hand side vector (n x 1)
    
    Returns:
        Solution vector x
    
    Raises:
        LinAlgError: If the matrix is singular or system cannot be solved
    """
    return np.linalg.solve(A, b)


def calculate_view_factors(surfaces: Dict[str, float]) -> Dict[str, float]:
    """
    Calculate view factors for radiation heat transfer.
    
    For simple geometries, uses analytical formulas. For complex geometries,
    would require Monte Carlo or other numerical methods.
    
    Args:
        surfaces: Dictionary of surface names and areas
    
    Returns:
        Dictionary of view factors (e.g., {'floor_to_ceiling': 0.5})
    """
    view_factors = {}
    
    # Simple parallel surfaces assumption
    total_area = sum(surfaces.values())
    
    for name1, area1 in surfaces.items():
        for name2, area2 in surfaces.items():
            if name1 != name2:
                # Simplified view factor based on area ratio
                key = f"{name1}_to_{name2}"
                view_factors[key] = area2 / total_area
    
    return view_factors


def solve_radiosity_system(
    view_factors: Dict[str, float],
    emissivities: Dict[str, float],
    temperatures: Dict[str, float],
    stefan_boltzmann: float = 5.67e-8
) -> Dict[str, float]:
    """
    Solve radiosity equation system [M][J] = [C].
    
    The radiosity method calculates radiation heat transfer between surfaces
    accounting for multiple reflections.
    
    Args:
        view_factors: Dictionary of view factors
        emissivities: Surface emissivities
        temperatures: Surface temperatures in K
        stefan_boltzmann: Stefan-Boltzmann constant
    
    Returns:
        Dictionary of radiosity values (W/m²)
    """
    surfaces = list(emissivities.keys())
    n = len(surfaces)
    
    # Build matrix M and vector C
    M = np.zeros((n, n))
    C = np.zeros(n)
    
    for i, surf_i in enumerate(surfaces):
        eps_i = emissivities[surf_i]
        T_i = temperatures[surf_i]
        
        # Emissive power
        C[i] = eps_i * stefan_boltzmann * (T_i ** 4)
        
        # Diagonal terms
        M[i, i] = 1.0
        
        # Off-diagonal terms (view factors)
        for j, surf_j in enumerate(surfaces):
            if i != j:
                key = f"{surf_i}_to_{surf_j}"
                F_ij = view_factors.get(key, 0.0)
                M[i, j] = -(1 - eps_i) * F_ij / eps_i
    
    # Solve for radiosity
    J = solve_linear_system(M, C)
    
    return {surf: float(J[i]) for i, surf in enumerate(surfaces)}


def solve_multi_zone_conduction(
    conductances: np.ndarray,
    temperatures: np.ndarray,
    heat_sources: np.ndarray
) -> np.ndarray:
    """
    Solve multi-zone heat transfer matrix equation.
    
    For a system with multiple thermal zones, solves:
    [K]{T} = {Q}
    
    Where:
    - K is the conductance matrix
    - T is the temperature vector
    - Q is the heat source vector
    
    Args:
        conductances: Thermal conductance matrix (n x n)
        temperatures: Initial temperature vector (n,) - for boundary conditions
        heat_sources: Heat source vector (n,)
    
    Returns:
        Solution temperature vector
    """
    return solve_linear_system(conductances, heat_sources)


def build_thermal_network_matrix(
    zones: List[str],
    conductances: Dict[Tuple[str, str], float],
    boundary_temps: Dict[str, float]
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Build thermal network matrix for multi-zone analysis.
    
    Args:
        zones: List of zone names
        conductances: Dictionary of conductances between zones
        boundary_temps: Dictionary of boundary temperatures
    
    Returns:
        Tuple of (conductance matrix, heat source vector)
    """
    n = len(zones)
    K = np.zeros((n, n))
    Q = np.zeros(n)
    
    for i, zone_i in enumerate(zones):
        # Sum conductances to zone i
        sum_conductances = 0.0
        
        for j, zone_j in enumerate(zones):
            if i != j:
                # Get conductance between zones
                key = (zone_i, zone_j)
                if key in conductances:
                    G_ij = conductances[key]
                elif (zone_j, zone_i) in conductances:
                    G_ij = conductances[(zone_j, zone_i)]
                else:
                    G_ij = 0.0
                
                K[i, j] = -G_ij
                sum_conductances += G_ij
        
        # Diagonal term
        K[i, i] = sum_conductances
        
        # Boundary conditions
        if zone_i in boundary_temps:
            Q[i] = sum_conductances * boundary_temps[zone_i]
    
    return K, Q
