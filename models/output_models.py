"""API 응답을 위한 Pydantic 모델"""

from pydantic import BaseModel, Field
from typing import List, Optional


class HourlyResult(BaseModel):
    """시간별 계산 결과"""
    
    hour: int = Field(..., description="시간 (0-23)")
    outdoor_temp: float = Field(..., description="외기 온도 (°C)")
    solar_radiation: float = Field(..., description="태양 복사 (W/m²)")
    conductive_loss: float = Field(..., description="전도 열손실 (W)")
    ventilation_loss: float = Field(..., description="환기 열손실 (W)")
    solar_gain: float = Field(..., description="태양열 취득 (W)")
    longwave_radiation: float = Field(..., description="장파 복사 (W)")
    radiation_heat_transfer: Optional[float] = Field(None, description="복사 열전달 (W)")
    net_load: float = Field(..., description="순 난방 부하 (W)")
    indoor_temp_dynamic: Optional[float] = Field(None, description="동적 실내 온도 (°C)")


class SimulationSummary(BaseModel):
    """시뮬레이션 요약 통계"""
    
    total_heating_load_kwh: float = Field(..., description="총 난방 부하 (kWh)")
    peak_load_w: float = Field(..., description="최대 부하 (W)")
    average_load_w: float = Field(..., description="평균 부하 (W)")
    floor_temperature: Optional[float] = Field(None, description="바닥 온도 (°C)")
    radiator_output: Optional[float] = Field(None, description="라디에이터 출력 (W)")


class FullSimulationResponse(BaseModel):
    """전체 난방 부하 시뮬레이션 응답 모델"""
    
    hourly_results: List[HourlyResult]
    summary: SimulationSummary


class SteadyStateResponse(BaseModel):
    """정상 상태 전도 계산 응답 모델"""
    
    conductive_loss: float = Field(..., description="총 전도 열손실 (W)")
    wall_loss: float = Field(..., description="벽 열손실 (W)")
    roof_loss: float = Field(..., description="지붕 열손실 (W)")
    floor_loss: float = Field(..., description="바닥 열손실 (W)")
    window_loss: float = Field(..., description="창문 열손실 (W)")
    ventilation_loss: float = Field(..., description="환기 열손실 (W)")
    total_loss: float = Field(..., description="총 열손실 (W)")


class RadiationResponse(BaseModel):
    """복사 열전달 계산 응답 모델"""
    
    radiative_flux: float = Field(..., description="복사 열유속 (W/m²)")
    floor_temperature: float = Field(..., description="바닥 온도 (°C)")
    view_factors: dict = Field(..., description="형태계수 딕셔너리")
    radiosity: dict = Field(..., description="복사도 값")


class TransientResponse(BaseModel):
    """과도 열 시뮬레이션 응답 모델"""

    hourly_temps: List[float] = Field(..., description="시간에 따른 실내 온도")
    hourly_loads: List[float] = Field(..., description="시간에 따른 난방 부하")
    final_temperature: float = Field(..., description="최종 실내 온도 (°C)")
    energy_stored: float = Field(..., description="열질량에 저장된 에너지 (J)")


class ClimateData(BaseModel):
    """시간별 기후 데이터 포인트"""

    hour: int = Field(..., description="시간 (0-24)")
    outdoor_temp: float = Field(..., description="외기 온도 (°C)")
    solar_radiation: float = Field(..., description="태양 복사 (W/m²)")
    sky_temp: float = Field(..., description="하늘 온도 (°C)")
    humidity: Optional[float] = Field(None, description="상대습도 (%)")
    direct_radiation: Optional[float] = Field(None, description="직달일사량 (W/m²)")
    diffuse_radiation: Optional[float] = Field(None, description="산란일사량 (W/m²)")
    cloud_cover: Optional[float] = Field(None, description="운량 (%)")
    data_type: Optional[str] = Field(None, description="데이터 유형 (observation/forecast)")


class ClimateResponse(BaseModel):
    """기후 데이터 생성 응답 모델"""

    climate_data: List[ClimateData]
    latitude: float
    longitude: float
