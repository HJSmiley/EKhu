"""
태양 복사 및 위치 계산 모듈 (Solar Radiation and Position Calculations)

이 모듈은 건축물의 일사 계산을 위한 태양 위치 및 복사량 함수를 제공합니다.
- 태양 적위각 계산
- 태양 시간각 계산
- 태양 고도각 및 방위각 계산
- 직달 일사량(DNI) 및 전천 일사량(GHI) 계산
- 경사면 일사량 계산
- 하늘 온도 계산 (장파복사용)

비정상 열전도 모델에서의 일사 항목 (5.2 공식): α × Isol
"""

import math
from typing import Tuple


def calculate_declination(day_of_year: int) -> float:
    """
    태양 적위각(Declination)을 계산합니다.

    공식: δ = 23.45 × sin((360/365)(284 + n))
    (Cooper 방정식)

    적위각은 태양 광선과 지구 적도면 사이의 각도입니다.
    하지(6월 21일경)에 +23.45°, 동지(12월 21일경)에 -23.45°입니다.

    매개변수:
        day_of_year: 연중 일수 n (1-365)

    반환값:
        적위각 δ (도, degrees)
    """
    return 23.45 * math.sin(math.radians((360 / 365) * (284 + day_of_year)))


def calculate_hour_angle(hour: int) -> float:
    """
    태양 시간각(Hour Angle)을 계산합니다.

    공식: H = (hour - 12) × 15°

    시간각은 태양의 정오로부터의 각변위입니다.
    지구는 시간당 15° 회전하므로 (360°/24h = 15°/h)
    오전은 음수, 오후는 양수입니다.

    매개변수:
        hour: 시각 (0-23, 태양시 기준)

    반환값:
        시간각 H (도, degrees)
    """
    return (hour - 12) * 15


def calculate_solar_elevation(
    latitude: float,
    declination: float,
    hour_angle: float
) -> float:
    """
    태양 고도각(Solar Elevation)을 계산합니다.

    공식: sin(α) = sin(φ)sin(δ) + cos(φ)cos(δ)cos(H)

    여기서:
        α: 태양 고도각 (수평면으로부터의 각도)
        φ: 위도
        δ: 적위각
        H: 시간각

    매개변수:
        latitude: 위도 φ (도)
        declination: 적위각 δ (도)
        hour_angle: 시간각 H (도)

    반환값:
        태양 고도각 α (라디안), 수평선 아래이면 0
    """
    lat_rad = math.radians(latitude)
    decl_rad = math.radians(declination)
    hour_rad = math.radians(hour_angle)

    sin_elev = (
        math.sin(lat_rad) * math.sin(decl_rad) +
        math.cos(lat_rad) * math.cos(decl_rad) * math.cos(hour_rad)
    )

    # 유효 범위로 제한하고 수평선 아래이면 0 반환
    sin_elev = max(-1.0, min(1.0, sin_elev))
    elevation = math.asin(sin_elev)

    return max(0.0, elevation)


def calculate_solar_radiation(
    solar_elevation: float,
    solar_constant: float = 1367.0,
    atmospheric_transmittance: float = 0.7
) -> Tuple[float, float]:
    """
    직달 일사량(DNI)과 전천 일사량(GHI)을 계산합니다. (5.2 공식 관련)

    DNI (Direct Normal Irradiance): 태양 광선에 수직인 면의 직달 일사량
    GHI (Global Horizontal Irradiance): 수평면 전천 일사량

    공식:
        대기 질량(Air Mass): AM = 1 / sin(α)
        대기 투과: τ_eff = τ^(AM^0.678)
        DNI = I₀ × τ_eff
        GHI = DNI × sin(α)

    매개변수:
        solar_elevation: 태양 고도각 α (라디안)
        solar_constant: 태양상수 I₀ (W/m², 기본값 1367.0)
        atmospheric_transmittance: 대기 투과율 τ (기본값 0.7)

    반환값:
        (DNI, GHI) 튜플 (W/m²)
    """
    if solar_elevation <= 0:
        return 0.0, 0.0

    # 대기 질량 계산 (Air Mass)
    air_mass = 1.0 / math.sin(solar_elevation)

    # 대기 투과 모델
    transmittance = atmospheric_transmittance ** (air_mass ** 0.678)

    # 직달 일사량 (Direct Normal Irradiance)
    DNI = solar_constant * transmittance

    # 전천 일사량 (Global Horizontal Irradiance)
    GHI = DNI * math.sin(solar_elevation)

    return DNI, max(0.0, GHI)


def calculate_sky_temperature(
    outdoor_temp: float,
    cloud_cover: float = 0.0,
    relative_humidity: float = 0.5
) -> float:
    """
    장파복사를 위한 유효 하늘 온도를 계산합니다. (4.1 공식 관련)

    하늘 온도는 대기의 장파복사 방출을 등가 흑체온도로 표현한 것입니다.
    창문을 통한 장파복사 열손실 계산에 사용됩니다. (4.1 공식)

    공식:
        맑은 하늘 온도 저하: ΔT_clear = 6 × (1 - 0.5 × RH)
        유효 온도 저하: ΔT_eff = ΔT_clear × (1 - 0.8 × CC)
        하늘 온도: T_sky = T_outdoor - ΔT_eff

    매개변수:
        outdoor_temp: 외기온도 Te (°C)
        cloud_cover: 운량 CC (0-1, 기본값 0.0)
        relative_humidity: 상대습도 RH (0-1, 기본값 0.5)

    반환값:
        하늘 온도 T_sky (°C)
    """
    # 맑은 하늘 온도 저하 (습도에 따라 변화)
    clear_sky_depression = 6.0 * (1.0 - relative_humidity * 0.5)

    # 운량이 온도 저하를 감소시킴
    effective_depression = clear_sky_depression * (1.0 - cloud_cover * 0.8)

    return outdoor_temp - effective_depression
