// Types for building parameters and simulation
export interface BuildingParams {
  // Building envelope
  wallArea: number; // m²
  wallUValue: number; // W/(m²·K)
  roofArea: number; // m²
  roofUValue: number; // W/(m²·K)
  floorArea: number; // m²
  floorUValue: number; // W/(m²·K)
  
  // Windows
  windowArea: number; // m²
  windowUValue: number; // W/(m²·K)
  shgc: number; // Solar Heat Gain Coefficient (0-1)
  
  // Ventilation
  ventilationRate: number; // ACH (Air Changes per Hour)
  buildingVolume: number; // m³
  
  // Indoor conditions
  indoorTemp: number; // °C
}

export interface ClimateData {
  latitude: number;
  longitude: number;
  temperature: number; // °C
  solarRadiation: number; // W/m²
  timestamp: Date;
}

export interface HourlyResult {
  hour: number;
  conductiveLoss: number; // W
  ventilationLoss: number; // W
  solarGain: number; // W
  longwaveRadiation: number; // W
  netLoad: number; // W
  outdoorTemp: number; // °C
  solarRadiation: number; // W/m²
}

export interface SimulationResult {
  hourlyResults: HourlyResult[];
  totalHeatingLoad: number; // kWh
  peakLoad: number; // W
  averageLoad: number; // W
}

// Constants
const AIR_DENSITY = 1.2; // kg/m³
const AIR_SPECIFIC_HEAT = 1005; // J/(kg·K)
const STEFAN_BOLTZMANN = 5.67e-8; // W/(m²·K⁴)
const GROUND_EMISSIVITY = 0.9;
const SKY_EMISSIVITY = 0.8;

/**
 * Calculate conductive heat loss through building envelope
 */
export function calculateConductiveLoss(
  params: BuildingParams,
  outdoorTemp: number
): number {
  const tempDiff = params.indoorTemp - outdoorTemp;
  
  const wallLoss = params.wallArea * params.wallUValue * tempDiff;
  const roofLoss = params.roofArea * params.roofUValue * tempDiff;
  const floorLoss = params.floorArea * params.floorUValue * tempDiff;
  const windowLoss = params.windowArea * params.windowUValue * tempDiff;
  
  return wallLoss + roofLoss + floorLoss + windowLoss;
}

/**
 * Calculate ventilation heat loss
 */
export function calculateVentilationLoss(
  params: BuildingParams,
  outdoorTemp: number
): number {
  const tempDiff = params.indoorTemp - outdoorTemp;
  const airFlowRate = (params.ventilationRate * params.buildingVolume) / 3600; // m³/s
  const massFlowRate = airFlowRate * AIR_DENSITY; // kg/s
  
  return massFlowRate * AIR_SPECIFIC_HEAT * tempDiff;
}

/**
 * Calculate solar heat gain through windows
 */
export function calculateSolarGain(
  params: BuildingParams,
  solarRadiation: number
): number {
  return params.windowArea * params.shgc * solarRadiation;
}

/**
 * Calculate longwave radiation heat exchange
 * Simplified model considering sky and ground radiation
 */
export function calculateLongwaveRadiation(
  params: BuildingParams,
  outdoorTemp: number
): number {
  const indoorTempK = params.indoorTemp + 273.15;
  const outdoorTempK = outdoorTemp + 273.15;
  
  // Simplified longwave radiation loss through windows
  // Assumes effective sky temperature is lower than outdoor air temperature
  const skyTempK = outdoorTempK - 10; // Simplified model
  
  const radiationLoss = params.windowArea * GROUND_EMISSIVITY * STEFAN_BOLTZMANN * 
    (Math.pow(indoorTempK, 4) - Math.pow(skyTempK, 4));
  
  return radiationLoss;
}

/**
 * Perform steady-state analysis for current conditions
 */
export function steadyStateAnalysis(
  params: BuildingParams,
  climateData: ClimateData
): {
  conductiveLoss: number;
  ventilationLoss: number;
  solarGain: number;
  longwaveRadiation: number;
  netLoad: number;
} {
  const conductiveLoss = calculateConductiveLoss(params, climateData.temperature);
  const ventilationLoss = calculateVentilationLoss(params, climateData.temperature);
  const solarGain = calculateSolarGain(params, climateData.solarRadiation);
  const longwaveRadiation = calculateLongwaveRadiation(params, climateData.temperature);
  
  const netLoad = conductiveLoss + ventilationLoss - solarGain + longwaveRadiation;
  
  return {
    conductiveLoss,
    ventilationLoss,
    solarGain,
    longwaveRadiation,
    netLoad
  };
}

/**
 * Generate synthetic hourly climate data for a typical winter day
 * In a real application, this would fetch actual climate data from an API
 */
export function generateHourlyClimateData(
  latitude: number,
  longitude: number,
  baseTemp: number = -5
): ClimateData[] {
  const hourlyData: ClimateData[] = [];
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  for (let hour = 0; hour < 24; hour++) {
    const timestamp = new Date(today);
    timestamp.setHours(hour);
    
    // Simplified diurnal temperature variation
    const tempVariation = -3 * Math.cos((hour - 14) * Math.PI / 12);
    const temperature = baseTemp + tempVariation;
    
    // Simplified solar radiation (peak at solar noon)
    let solarRadiation = 0;
    if (hour >= 6 && hour <= 18) {
      const solarAngle = Math.sin((hour - 6) * Math.PI / 12);
      solarRadiation = 800 * Math.max(0, solarAngle);
    }
    
    hourlyData.push({
      latitude,
      longitude,
      temperature,
      solarRadiation,
      timestamp
    });
  }
  
  return hourlyData;
}

/**
 * Run hourly simulation for 24 hours
 */
export function runHourlySimulation(
  params: BuildingParams,
  climateData: ClimateData[]
): SimulationResult {
  const hourlyResults: HourlyResult[] = [];
  let totalEnergyWh = 0;
  let peakLoad = 0;
  
  for (let i = 0; i < climateData.length; i++) {
    const data = climateData[i];
    const analysis = steadyStateAnalysis(params, data);
    
    const result: HourlyResult = {
      hour: i,
      conductiveLoss: analysis.conductiveLoss,
      ventilationLoss: analysis.ventilationLoss,
      solarGain: analysis.solarGain,
      longwaveRadiation: analysis.longwaveRadiation,
      netLoad: Math.max(0, analysis.netLoad), // Only heating load
      outdoorTemp: data.temperature,
      solarRadiation: data.solarRadiation
    };
    
    hourlyResults.push(result);
    totalEnergyWh += result.netLoad;
    peakLoad = Math.max(peakLoad, result.netLoad);
  }
  
  const totalHeatingLoad = totalEnergyWh / 1000; // Convert Wh to kWh
  const averageLoad = totalEnergyWh / climateData.length;
  
  return {
    hourlyResults,
    totalHeatingLoad,
    peakLoad,
    averageLoad
  };
}
