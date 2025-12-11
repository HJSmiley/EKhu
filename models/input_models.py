"""입력 검증을 위한 Pydantic 모델"""

from pydantic import BaseModel, Field
from typing import Optional


class BuildingParams(BaseModel):
    """건물 외피 및 시스템 매개변수"""
    
    wall_area: float = Field(..., gt=0, description="벽 면적 (m²)")
    wall_u_value: float = Field(..., gt=0, description="벽 열관류율 (W/m²·K)")
    roof_area: float = Field(..., gt=0, description="지붕 면적 (m²)")
    roof_u_value: float = Field(..., gt=0, description="지붕 열관류율 (W/m²·K)")
    floor_area: float = Field(..., gt=0, description="바닥 면적 (m²)")
    floor_u_value: float = Field(..., gt=0, description="바닥 열관류율 (W/m²·K)")
    window_area: float = Field(..., gt=0, description="창문 면적 (m²)")
    window_u_value: float = Field(..., gt=0, description="창문 열관류율 (W/m²·K)")
    shgc: float = Field(..., ge=0, le=1, description="태양열 취득 계수")
    ventilation_rate: float = Field(..., gt=0, description="환기율 (ACH)")
    building_volume: float = Field(..., gt=0, description="건물 체적 (m³)")
    indoor_temp: float = Field(..., description="실내 온도 (°C)")
    
    # 고급 계산을 위한 선택적 매개변수
    emissivity: Optional[float] = Field(0.85, ge=0, le=1, description="표면 방사율")


class ClimateParams(BaseModel):
    """기후 위치 및 시간 매개변수"""

    latitude: float = Field(..., ge=-90, le=90, description="위도 (도)")
    longitude: float = Field(..., ge=-180, le=180, description="경도 (도)")


class SimulationOptions(BaseModel):
    """시뮬레이션 구성 옵션"""
    
    include_radiation: bool = Field(True, description="복사 열전달 포함")
    include_transient: bool = Field(True, description="과도 효과 포함")
    timestep_seconds: int = Field(3600, gt=0, description="시뮬레이션 시간 간격 (초)")


class FullSimulationRequest(BaseModel):
    """전체 난방 부하 시뮬레이션 요청 모델"""
    
    building: BuildingParams
    climate: ClimateParams
    simulation_options: Optional[SimulationOptions] = SimulationOptions()


class SteadyStateRequest(BaseModel):
    """정상 상태 전도 계산 요청 모델"""
    
    building: BuildingParams
    climate: ClimateParams


class RadiationRequest(BaseModel):
    """복사 열전달 계산 요청 모델"""
    
    building: BuildingParams
    climate: ClimateParams


class TransientRequest(BaseModel):
    """과도 열 시뮬레이션 요청 모델"""

    building: BuildingParams
    climate: ClimateParams
    simulation_options: Optional[SimulationOptions] = SimulationOptions()
