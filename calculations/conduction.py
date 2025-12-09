"""
정상상태 열전도 계산 모듈 (Steady-state Conduction Heat Transfer)

이 모듈은 건축물의 정상상태 열전달 계산을 위한 함수들을 제공합니다.
- 열저항 계산
- 열관류율(U-value) 계산
- 전도 열손실 계산
- 환기 열손실 계산
- 다실 열평형 계산
"""

from typing import Dict

# 물리 상수 (Physical Constants)

AIR_DENSITY = 1.2       # 공기 밀도 ρ (kg/m³)
SPECIFIC_HEAT_AIR = 1000  # 공기 비열 cp (J/kg·K) - 수업 공식 기준


def calculate_conductive_loss(
    area: float,
    u_value: float,
    indoor_temp: float,
    outdoor_temp: float
) -> float:
    """
    건물 부위를 통한 전도 열손실을 계산합니다. (1.4 공식)

    공식: Φ = D × ΔT = (U × A) × (Ti - Te)
    여기서 D = U × A 는 열관류량 (1.2 공식)

    매개변수:
        area: 표면적 A (m²)
        u_value: 열관류율 U (W/m²·K)
        indoor_temp: 실내온도 Ti (°C)
        outdoor_temp: 외기온도 Te (°C)

    반환값:
        열손실량 Φ (W)
    """
    # 온도차 계산: ΔT = Ti - Te
    delta_t = indoor_temp - outdoor_temp
    # 열손실 = 면적 × 열관류율 × 온도차 (1.4 공식)
    return area * u_value * delta_t


def calculate_ventilation_loss(
    building_volume: float,
    ventilation_rate: float,
    indoor_temp: float,
    outdoor_temp: float
) -> float:
    """
    환기에 의한 열손실을 계산합니다. (1.3 공식, 2.1 공식)

    공식: Φ = ṁ × cp × ΔT
    여기서 ṁ = ρ × V × ACH / 3600 (2.1 공식)

    환기 열손실 계수: D_vent = V̇ × cp × ρ / 3600 (1.3 공식)
    여기서 V̇ = V × ACH (환기량, m³/h)

    매개변수:
        building_volume: 건물 체적 V (m³)
        ventilation_rate: 시간당 환기횟수 ACH (회/h)
        indoor_temp: 실내온도 Ti (°C)
        outdoor_temp: 외기온도 Te (°C)

    반환값:
        환기 열손실량 Φ (W)
    """
    # 질량유량 계산: ṁ = ρ × V × ACH / 3600 (2.1 공식)
    mass_flow = (AIR_DENSITY * building_volume * ventilation_rate) / 3600
    # 온도차 계산
    delta_t = indoor_temp - outdoor_temp
    # 환기 열손실 = 질량유량 × 비열 × 온도차 (1.3 공식)
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
    건물의 총 열손실을 계산합니다. (1.4 공식)

    공식: Φ_tot = D_tot × (Ti - Te)
    여기서 D_tot = Σ(U × A) + D_vent

    매개변수:
        wall_area: 벽체 면적 (m²)
        wall_u_value: 벽체 열관류율 (W/m²·K)
        roof_area: 지붕 면적 (m²)
        roof_u_value: 지붕 열관류율 (W/m²·K)
        floor_area: 바닥 면적 (m²)
        floor_u_value: 바닥 열관류율 (W/m²·K)
        window_area: 창문 면적 (m²)
        window_u_value: 창문 열관류율 (W/m²·K)
        building_volume: 건물 체적 (m³)
        ventilation_rate: 환기횟수 ACH (회/h)
        indoor_temp: 실내온도 Ti (°C)
        outdoor_temp: 외기온도 Te (°C)

    반환값:
        각 부위별 및 총 열손실을 담은 딕셔너리 (W)
    """
    # 각 부위별 전도 열손실 계산 (1.4 공식)
    wall_loss = calculate_conductive_loss(wall_area, wall_u_value, indoor_temp, outdoor_temp)
    roof_loss = calculate_conductive_loss(roof_area, roof_u_value, indoor_temp, outdoor_temp)
    floor_loss = calculate_conductive_loss(floor_area, floor_u_value, indoor_temp, outdoor_temp)
    window_loss = calculate_conductive_loss(window_area, window_u_value, indoor_temp, outdoor_temp)

    # 총 전도 열손실 = 벽체 + 지붕 + 바닥 + 창문
    conductive_loss = wall_loss + roof_loss + floor_loss + window_loss

    # 환기 열손실 계산 (1.3 공식)
    ventilation_loss = calculate_ventilation_loss(
        building_volume, ventilation_rate, indoor_temp, outdoor_temp
    )

    # 총 열부하 = 전도 열손실 + 환기 열손실 (1.4 공식)
    total_loss = conductive_loss + ventilation_loss

    return {
        'wall_loss': wall_loss,           # 벽체 열손실 (W)
        'roof_loss': roof_loss,           # 지붕 열손실 (W)
        'floor_loss': floor_loss,         # 바닥 열손실 (W)
        'window_loss': window_loss,       # 창문 열손실 (W)
        'conductive_loss': conductive_loss,  # 총 전도 열손실 (W)
        'ventilation_loss': ventilation_loss,  # 환기 열손실 (W)
        'total_loss': total_loss          # 총 열손실 (W)
    }
