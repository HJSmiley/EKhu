// ==========================================================================
//  Building Heating Load Calculation Engine
//  Fully Refactored with Latitude/Longitude Based Climate Model
// ==========================================================================

// ------------------------------
// Type Definitions
// ------------------------------

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
  solarElevationDeg: number;
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

// ==========================================================================
//  Climate Model (Latitude / Longitude Based)
// ==========================================================================

// 태양 적위각 (Declination Angle)
function getDeclination(dayOfYear: number) {
  return 23.45 * Math.sin(((360 / 365) * (284 + dayOfYear)) * (Math.PI / 180));
}

// 시간각 (Hour Angle)
function getHourAngle(hour: number) {
  return (hour - 12) * 15; // 1시간 = 15도
}

// 태양 고도각 (Solar Elevation Angle)
function getSolarElevation(lat: number, decl: number, hourAngle: number) {
  const latRad = (lat * Math.PI) / 180;
  const declRad = (decl * Math.PI) / 180;
  const hrRad = (hourAngle * Math.PI) / 180;

  const sinElev =
    Math.sin(latRad) * Math.sin(declRad) +
    Math.cos(latRad) * Math.cos(declRad) * Math.cos(hrRad);

  return Math.max(0, Math.asin(sinElev)); // 음수면 일사 없음 (지평선 아래)
}

// 태양 복사량 모델
function getSolarRadiation(solarElevation: number) {
  const I_sc = 1367; // Solar constant W/m²
  if (solarElevation <= 0) return 0;

  // 대기 감쇠 (Air mass model)
  const airMass = 1 / Math.sin(solarElevation);
  const transmittance = 0.7 ** (airMass ** 0.678);

  const DNI = I_sc * transmittance; // Direct Normal Irradiance
  const GHI = DNI * Math.sin(solarElevation); // Global Horizontal Irradiance

  return Math.max(0, GHI);
}

// 외기온 모델 (Latitude 기반)
function getOutdoorTemp(hour: number, latitude: number) {
  // 한국 위도 기준 서울 lat=37 -> -5°C 를 기본값
  const baseTemp = -5 - Math.abs(latitude - 37) * 0.7;

  const dailyAmplitude = 6; // 일교차
  const temp =
    baseTemp +
    dailyAmplitude * Math.sin(((hour - 8) / 24) * 2 * Math.PI);

  return temp;
}

// Sky Temperature (장파복사용)
function getSkyTemp(outdoorTemp: number) {
  return outdoorTemp - 6; // 간단 모델
}

// ==========================================================================
//   Public Function: generateHourlyClimateData
// ==========================================================================

export function generateHourlyClimateData(latitude: number, longitude: number): HourlyClimateData[] {
  const dayOfYear = 15; // 1월 15일 (난방 부하 peak 시기)
  const decl = getDeclination(dayOfYear);

  const climateData: HourlyClimateData[] = [];

  for (let hour = 0; hour < 24; hour++) {
    const hourAngle = getHourAngle(hour);
    const solarElevation = getSolarElevation(latitude, decl, hourAngle);
    const solarRadiation = getSolarRadiation(solarElevation);
    const outdoorTemp = getOutdoorTemp(hour, latitude);
    const skyTemp = getSkyTemp(outdoorTemp);

    climateData.push({
      hour,
      outdoorTemp,
      solarRadiation,
      skyTemp,
      solarElevationDeg: (solarElevation * 180) / Math.PI,
    });
  }

  return climateData;
}

// ==========================================================================
//  Heating Load Simulation Model
// ==========================================================================

const AIR_DENSITY = 1.2; // kg/m³
const SPECIFIC_HEAT_AIR = 1005; // J/kg·K
const STEFAN_BOLTZMANN = 5.67e-8; // W/m²·K⁴

// 주요 계산 엔진
export function runHourlySimulation(
  params: BuildingParams,
  climateData: HourlyClimateData[]
): SimulationResult {
  const results: HourlyResult[] = [];

  for (let hour = 0; hour < 24; hour++) {
    const climate = climateData[hour];

    const deltaT = params.indoorTemp - climate.outdoorTemp;

    // ① Conductive Loss
    const conductiveLoss =
      params.wallArea * params.wallUValue * deltaT +
      params.roofArea * params.roofUValue * deltaT +
      params.floorArea * params.floorUValue * deltaT +
      params.windowArea * params.windowUValue * deltaT;

    // ② Ventilation Loss (ACH 기반)
    const massFlow =
      (AIR_DENSITY * params.buildingVolume * params.ventilationRate) / 3600;
    const ventilationLoss = massFlow * SPECIFIC_HEAT_AIR * deltaT;

    // ③ Solar Gain
    const solarGain =
      params.windowArea * params.shgc * climate.solarRadiation;

    // ④ Longwave Radiation
    const T_in_K = params.indoorTemp + 273.15;
    const T_sky_K = climate.skyTemp + 273.15;
    const longwaveRadiation =
      0.9 * STEFAN_BOLTZMANN * params.windowArea * (T_in_K ** 4 - T_sky_K ** 4);

    // ⑤ Net Heating Load
    const netLoad =
      conductiveLoss + ventilationLoss - solarGain + longwaveRadiation;

    results.push({
      hour,
      outdoorTemp: climate.outdoorTemp,
      solarRadiation: climate.solarRadiation,
      conductiveLoss,
      ventilationLoss,
      solarGain,
      longwaveRadiation,
      netLoad,
    });
  }

  // Summary Stats
  const hourlyLoads = results.map((r) => r.netLoad);
  const totalHeatingLoad = hourlyLoads.reduce((a, b) => a + b, 0) / 1000 / 1; // Wh → kWh/day
  const peakLoad = Math.max(...hourlyLoads);
  const averageLoad = peakLoad / 24;

  return {
    hourlyResults: results,
    totalHeatingLoad,
    peakLoad,
    averageLoad,
  };
}
