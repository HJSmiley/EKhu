/**
 * API client for Python FastAPI backend
 */

import { BuildingParams } from '../heatingLoad';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export interface ClimateParams {
  latitude: number;
  longitude: number;
  day_of_year: number;
}

export interface SimulationOptions {
  include_radiation: boolean;
  include_transient: boolean;
  timestep_seconds: number;
}

export interface HourlyResult {
  hour: number;
  outdoor_temp: number;
  solar_radiation: number;
  conductive_loss: number;
  ventilation_loss: number;
  solar_gain: number;
  longwave_radiation: number;
  radiation_heat_transfer?: number;
  net_load: number;
  indoor_temp_dynamic?: number;
}

export interface SimulationSummary {
  total_heating_load_kwh: number;
  peak_load_w: number;
  average_load_w: number;
  floor_temperature?: number;
  radiator_output?: number;
}

export interface FullSimulationResponse {
  hourly_results: HourlyResult[];
  summary: SimulationSummary;
}

export interface SteadyStateResponse {
  conductive_loss: number;
  wall_loss: number;
  roof_loss: number;
  floor_loss: number;
  window_loss: number;
  ventilation_loss: number;
  total_loss: number;
}

export interface RadiationResponse {
  radiative_flux: number;
  floor_temperature: number;
  view_factors: Record<string, number>;
  radiosity: Record<string, number>;
}

export interface TransientResponse {
  hourly_temps: number[];
  hourly_loads: number[];
  final_temperature: number;
  energy_stored: number;
}

export interface GlasshouseResponse {
  interior_temp: number;
  glass_temp: number;
  collector_temp: number;
  heating_load: number;
  solar_absorbed: number;
  iterations: number;
}

export interface ClimateData {
  hour: number;
  outdoor_temp: number;
  solar_radiation: number;
  sky_temp: number;
  solar_elevation_deg: number;
}

export interface ClimateResponse {
  climate_data: ClimateData[];
  latitude: number;
  longitude: number;
  day_of_year: number;
}

/**
 * Convert BuildingParams to backend format
 */
function convertBuildingParams(params: BuildingParams) {
  return {
    wall_area: params.wallArea,
    wall_u_value: params.wallUValue,
    roof_area: params.roofArea,
    roof_u_value: params.roofUValue,
    floor_area: params.floorArea,
    floor_u_value: params.floorUValue,
    window_area: params.windowArea,
    window_u_value: params.windowUValue,
    shgc: params.shgc,
    ventilation_rate: params.ventilationRate,
    building_volume: params.buildingVolume,
    indoor_temp: params.indoorTemp,
    emissivity: 0.85,
    reflectivity: 0.15,
    thermal_capacity: 1e7,
    thermal_resistance: 8e-3
  };
}

/**
 * Calculate full heating load simulation
 */
export async function calculateHeatingLoad(
  params: BuildingParams,
  climate: ClimateParams,
  options?: SimulationOptions
): Promise<FullSimulationResponse> {
  const response = await fetch(`${BACKEND_URL}/api/v1/heating-load/full-simulation`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      building: convertBuildingParams(params),
      climate,
      simulation_options: options || {
        include_radiation: true,
        include_transient: true,
        timestep_seconds: 3600
      }
    })
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

/**
 * Calculate steady-state heat loss
 */
export async function calculateSteadyState(
  params: BuildingParams,
  climate: ClimateParams
): Promise<SteadyStateResponse> {
  const response = await fetch(`${BACKEND_URL}/api/v1/heating-load/steady-state`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      building: convertBuildingParams(params),
      climate
    })
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

/**
 * Calculate radiation heat transfer
 */
export async function calculateRadiation(
  params: BuildingParams,
  climate: ClimateParams
): Promise<RadiationResponse> {
  const response = await fetch(`${BACKEND_URL}/api/v1/heating-load/radiation`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      building: convertBuildingParams(params),
      climate
    })
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

/**
 * Calculate transient thermal response
 */
export async function calculateTransient(
  params: BuildingParams,
  climate: ClimateParams,
  options?: SimulationOptions
): Promise<TransientResponse> {
  const response = await fetch(`${BACKEND_URL}/api/v1/heating-load/transient`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      building: convertBuildingParams(params),
      climate,
      simulation_options: options
    })
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

/**
 * Calculate glasshouse/passive solar heating
 */
export async function calculateGlasshouse(
  params: BuildingParams,
  climate: ClimateParams
): Promise<GlasshouseResponse> {
  const response = await fetch(`${BACKEND_URL}/api/v1/heating-load/glasshouse`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      building: convertBuildingParams(params),
      climate
    })
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

/**
 * Generate climate data for a location
 */
export async function generateClimateData(
  latitude: number,
  longitude: number,
  dayOfYear: number = 15
): Promise<ClimateResponse> {
  const response = await fetch(
    `${BACKEND_URL}/api/v1/climate/generate?latitude=${latitude}&longitude=${longitude}&day_of_year=${dayOfYear}`
  );

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

/**
 * Check if backend is available
 */
export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${BACKEND_URL}/health`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });
    return response.ok;
  } catch (error) {
    return false;
  }
}
