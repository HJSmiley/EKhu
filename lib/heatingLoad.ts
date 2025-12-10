// ==========================================================================
//  Type Definitions for Building Heating Load Calculations
//  Note: Actual calculations are performed by the Python backend
// ==========================================================================

export interface BuildingParams {
  wallArea: number;
  wallUValue: number;
  roofArea: number;
  roofUValue: number;
  floorArea: number;
  floorUValue: number;
  windowArea: number;
  windowUValue: number;
  shgc: number;
  ventilationRate: number; // ACH
  buildingVolume: number; // m³
  indoorTemp: number; // °C
}

export interface HourlyClimateData {
  hour: number;
  outdoorTemp: number;
  solarRadiation: number;
  skyTemp: number;
  humidity?: number;
  directRadiation?: number;
  diffuseRadiation?: number;
  cloudCover?: number;
  dataType?: 'observation' | 'forecast';
}

export interface HourlyResult {
  hour: number;
  outdoorTemp: number;
  solarRadiation: number;
  conductiveLoss: number;
  ventilationLoss: number;
  solarGain: number;
  longwaveRadiation: number;
  netLoad: number;
}

export interface SimulationResult {
  hourlyResults: HourlyResult[];
  totalHeatingLoad: number;
  peakLoad: number;
  averageLoad: number;
}
