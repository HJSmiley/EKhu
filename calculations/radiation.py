"""
복사열전달 계산 모듈 (Radiation Heat Transfer with View Factors)

이 모듈은 건축물의 복사열전달 계산을 위한 함수들을 제공합니다.
- Stefan-Boltzmann 법칙 기반 복사열전달 (4.1 공식)
- 형상계수(View Factor) 계산 (4.2, 4.3 공식)
- 복사도(Radiosity) 방법을 이용한 다중 표면 복사교환 (4.4 공식)
- 표면 온도 계산 (4.5 공식)
"""

import math
from typing import Dict
from calculations.matrix_solver import calculate_view_factors, solve_radiosity_system


# ============================================================================
# 물리 상수 (Physical Constants)
# ============================================================================
# Stefan-Boltzmann 상수 σ (4.1 공식)
STEFAN_BOLTZMANN = 5.67e-8  # W/m²·K⁴


def solve_radiation_exchange(
    surfaces: Dict[str, Dict],
    ambient_temp: float = 20.0
) -> Dict[str, float]:
    """
    다중 표면 간의 복사교환을 풀이합니다. (4.4 공식)

    복사도(Radiosity) 방법을 사용하여 다중 반사를 고려합니다.

    표면 순열유속 (4.4 공식): Φ = A × (ε/ρ) × (σT⁴ - J)
    여기서:
        J: 복사도 (Radiosity, W/m²)
        ρ: 반사율 (= 1 - ε)

    매개변수:
        surfaces: 표면 속성 딕셔너리
                  각 표면은 area(면적), emissivity(방사율), temperature(온도) 포함
        ambient_temp: 주변 온도 (°C, 기본값 20.0)

    반환값:
        각 표면의 복사도(radiosity)와 순열유속(net_flux)을 담은 딕셔너리
    """
    # 표면 속성 추출
    surface_names = list(surfaces.keys())
    areas = {name: props['area'] for name, props in surfaces.items()}
    emissivities = {name: props['emissivity'] for name, props in surfaces.items()}

    # 온도를 절대온도(K)로 변환
    temperatures = {
        name: props.get('temperature', ambient_temp) + 273.15
        for name, props in surfaces.items()
    }

    # 형상계수 계산 (4.2, 4.3 공식)
    view_factors = calculate_view_factors(areas)

    # 복사도 시스템 풀이
    radiosities = solve_radiosity_system(
        view_factors, emissivities, temperatures, STEFAN_BOLTZMANN
    )

    # 각 표면의 순복사 열유속 계산 (4.4 공식)
    results = {}
    for name in surface_names:
        eps = emissivities[name]  # 방사율 ε
        T = temperatures[name]    # 절대온도 (K)
        J = radiosities[name]     # 복사도 J (W/m²)

        # 방사력: E = ε × σ × T⁴ (4.1 공식)
        E = eps * STEFAN_BOLTZMANN * (T ** 4)
        # 순열유속: q = (E - J) × ε / (1 - ε) (4.4 공식)
        # 여기서 (1 - ε) = ρ (반사율)
        q = (E - J) * eps / (1 - eps) if eps < 1.0 else 0.0

        results[name] = {
            'radiosity': J,        # 복사도 (W/m²)
            'net_flux': q,         # 순열유속 (W/m²)
            'emissive_power': E    # 방사력 (W/m²)
        }

    return results


def calculate_floor_temperature_from_radiosity(
    radiosity: float,
    emissivity: float,
    convective_coeff: float,
    air_temp: float,
    radiative_sources: float = 0.0
) -> float:
    """
    복사도 평형으로부터 바닥 온도를 계산합니다. (4.5 공식)

    에너지 평형: 복사교환 + 대류 + 내부열원 = 0

    단열 표면 온도 (4.5 공식): T = (J/σ)^(1/4)
    (단, 이 함수는 대류와 열원을 고려한 확장 버전)

    매개변수:
        radiosity: 바닥 복사도 J (W/m²)
        emissivity: 바닥 방사율 ε
        convective_coeff: 대류열전달 계수 h (W/m²·K)
        air_temp: 공기온도 (°C)
        radiative_sources: 추가 복사열원 (W/m², 기본값 0.0)

    반환값:
        바닥온도 (°C)
    """
    # 바닥 온도에 대한 반복 해법
    T_floor = air_temp  # 초기 추정값

    for _ in range(50):  # 최대 반복횟수
        T_floor_K = T_floor + 273.15

        # 방사력: E = ε × σ × T⁴ (4.1 공식)
        E = emissivity * STEFAN_BOLTZMANN * (T_floor_K ** 4)

        # 순복사 열유속 (4.4 공식)
        q_rad = (E - radiosity) * emissivity / (1 - emissivity) if emissivity < 1.0 else 0.0

        # 대류 열유속
        q_conv = convective_coeff * (T_floor - air_temp)

        # 에너지 평형 잔차
        residual = q_rad + q_conv - radiative_sources

        # 수렴 확인
        if abs(residual) < 0.1:
            break

        # 온도 업데이트 (Newton-Raphson 방법)
        T_floor -= residual / (4 * emissivity * STEFAN_BOLTZMANN * (T_floor_K ** 3) + convective_coeff)

    return T_floor


def calculate_longwave_radiation_to_sky(
    window_area: float,
    emissivity: float,
    indoor_temp: float,
    sky_temp: float
) -> float:
    """
    창문을 통한 하늘로의 장파복사 열손실을 계산합니다. (4.1 공식)

    공식: Q = ε × σ × A × (Ti⁴ - Tsky⁴) (4.1 공식 적용)

    매개변수:
        window_area: 창문 면적 A (m²)
        emissivity: 유효 방사율 ε
        indoor_temp: 실내온도 Ti (°C)
        sky_temp: 하늘온도 Tsky (°C)

    반환값:
        장파복사 열손실 Q (W)
    """
    # 섭씨를 절대온도(K)로 변환
    T1_K = indoor_temp + 273.15
    T2_K = sky_temp + 273.15

    # 복사열전달량 = ε × σ × A × (T₁⁴ - T₂⁴) (4.1 공식)
    return emissivity * STEFAN_BOLTZMANN * window_area * (T1_K**4 - T2_K**4)
