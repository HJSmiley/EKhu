"""
유리온실 및 패시브 태양열 난방 계산 모듈 (Glasshouse and Passive Solar Heating)

이 모듈은 유리온실의 열평형 및 패시브 태양열 시스템 계산을 제공합니다.
- 복사열전달 계수 계산
- 유리온실 온도 해석
- 난방부하 계산
- 패시브 태양열 획득량 계산
- 유리온실 최적 설계
"""

import numpy as np
from typing import Tuple, Dict


# ============================================================================
# 물리 상수 (Physical Constants)
# ============================================================================
# Stefan-Boltzmann 상수 σ (4.1 공식)
STEFAN_BOLTZMANN = 5.67e-8  # W/m²·K⁴


def solve_glasshouse_temperatures(
    T_outdoor: float,
    solar_irradiance: float,
    glass_area: float,
    collector_area: float,
    glass_transmittance: float = 0.85,
    glass_absorptance: float = 0.05,
    collector_absorptance: float = 0.90,
    emissivity_glass: float = 0.90,
    emissivity_collector: float = 0.85,
    emissivity_interior: float = 0.90,
    h_conv_ext: float = 15.0,
    h_conv_int: float = 5.0,
    U_back: float = 0.5,
    max_iterations: int = 100,
    tolerance: float = 0.01
) -> Tuple[float, float, float, int]:
    """
    유리온실의 열평형을 반복 행렬 해법으로 풀이합니다. (2.2 공식, 4.1 공식 기반)

    열평형 방정식 (Matrix 형태): [A][T] = [b] (2.2 공식)

    에너지 평형 방정식:
    1. 실내: 유리로부터의 대류 + 집열판으로부터의 복사 = 후면 열손실
    2. 유리: 일사흡수 + 복사교환 = 외부/내부로의 대류
    3. 집열판: 일사흡수 = 유리로의 복사 + 실내로의 대류

    복사열전달: Stefan-Boltzmann 법칙 적용 (4.1 공식)

    매개변수:
        T_outdoor: 외기온도 (°C)
        solar_irradiance: 일사량 (W/m²)
        glass_area: 유리 면적 (m²)
        collector_area: 집열판 면적 (m²)
        glass_transmittance: 유리 일사투과율 τ (기본값 0.85)
        glass_absorptance: 유리 일사흡수율 α (기본값 0.05)
        collector_absorptance: 집열판 일사흡수율 α (기본값 0.90)
        emissivity_glass: 유리 방사율 ε (기본값 0.90)
        emissivity_collector: 집열판 방사율 ε (기본값 0.85)
        emissivity_interior: 실내표면 방사율 ε (기본값 0.90)
        h_conv_ext: 외부 대류열전달계수 (W/m²·K, 기본값 15.0)
        h_conv_int: 내부 대류열전달계수 (W/m²·K, 기본값 5.0)
        U_back: 후면벽 열관류율 (W/m²·K, 기본값 0.5)
        max_iterations: 최대 반복횟수 (기본값 100)
        tolerance: 수렴 허용오차 (K, 기본값 0.01)

    반환값:
        (실내온도, 유리온도, 집열판온도, 반복횟수) 튜플 (°C)
    """
    # 초기 추정값 (절대온도 K로 변환)
    T_i = T_outdoor + 10 + 273.15  # 실내온도 초기값
    T_g = T_outdoor + 5 + 273.15   # 유리온도 초기값
    T_c = T_outdoor + 15 + 273.15  # 집열판온도 초기값
    T_e = T_outdoor + 273.15       # 외기온도 (K)

    # 일사에 의한 열획득량 계산
    Q_glass_solar = glass_absorptance * solar_irradiance * glass_area  # 유리 일사흡수
    Q_collector_solar = collector_absorptance * glass_transmittance * solar_irradiance * collector_area  # 집열판 일사흡수

    for iteration in range(max_iterations):
        # 복사열전달 계수 계산 (4.1 공식 기반)
        # 선형화된 복사계수 = ε × σ × (T₁² + T₂²) × (T₁ + T₂)
        hr_gc = emissivity_glass * emissivity_collector * STEFAN_BOLTZMANN * (T_g**2 + T_c**2) * (T_g + T_c)
        hr_gi = emissivity_glass * emissivity_interior * STEFAN_BOLTZMANN * (T_g**2 + T_i**2) * (T_g + T_i)
        hr_ci = emissivity_collector * emissivity_interior * STEFAN_BOLTZMANN * (T_c**2 + T_i**2) * (T_c + T_i)

        # 계수 행렬 [A]와 상수 벡터 [b] 구성 (2.2 공식)
        # 시스템: [A] × [T_i, T_g, T_c]ᵀ = [b]

        # 방정식 1: 실내 에너지 평형
        # h_conv_int × (T_g - T_i) + hr_ci × (T_c - T_i) = U_back × (T_i - T_e)
        a11 = h_conv_int + hr_ci + U_back
        a12 = -h_conv_int
        a13 = -hr_ci
        b1 = U_back * T_e

        # 방정식 2: 유리 에너지 평형
        # Q_glass_solar + h_conv_ext × (T_e - T_g) + hr_gi × (T_i - T_g) + hr_gc × (T_c - T_g) = 0
        a21 = -hr_gi
        a22 = h_conv_ext + hr_gi + hr_gc
        a23 = -hr_gc
        b2 = Q_glass_solar + h_conv_ext * T_e

        # 방정식 3: 집열판 에너지 평형
        # Q_collector_solar = hr_gc × (T_c - T_g) + hr_ci × (T_c - T_i)
        a31 = -hr_ci
        a32 = -hr_gc
        a33 = hr_gc + hr_ci
        b3 = Q_collector_solar

        # 선형 시스템 풀이: [A][T] = [b] (2.2 공식)
        A = np.array([
            [a11, a12, a13],
            [a21, a22, a23],
            [a31, a32, a33]
        ])
        b = np.array([b1, b2, b3])

        try:
            T_new = np.linalg.solve(A, b)
        except np.linalg.LinAlgError:
            # 행렬이 특이(singular)한 경우 이전 값 사용
            break

        T_i_new, T_g_new, T_c_new = T_new

        # 수렴 확인
        max_change = max(
            abs(T_i_new - T_i),
            abs(T_g_new - T_g),
            abs(T_c_new - T_c)
        )

        if max_change < tolerance:
            T_i, T_g, T_c = T_i_new, T_g_new, T_c_new
            break

        # 완화계수를 적용하여 온도 업데이트 (수렴 안정성 확보)
        relax = 0.5  # 완화계수
        T_i = T_i + relax * (T_i_new - T_i)
        T_g = T_g + relax * (T_g_new - T_g)
        T_c = T_c + relax * (T_c_new - T_c)

    # 섭씨로 변환하여 반환
    return (T_i - 273.15, T_g - 273.15, T_c - 273.15, iteration + 1)


def calculate_passive_solar_gain(
    glass_area: float,
    glass_transmittance: float,
    solar_irradiance: float,
    collector_area: float,
    collector_absorptance: float
) -> float:
    """
    유리온실을 통한 총 패시브 태양열 획득량을 계산합니다. (5.2 공식 관련)

    일사 획득량 계산 (5.2 공식의 α × Isol 항목과 유사)
    Q = τ × I × A (투과) + α × τ × I × A (흡수)

    매개변수:
        glass_area: 유리 면적 A (m²)
        glass_transmittance: 유리 일사투과율 τ
        solar_irradiance: 일사량 Isol (W/m²)
        collector_area: 집열판 면적 (m²)
        collector_absorptance: 집열판 일사흡수율 α

    반환값:
        총 태양열 획득량 Q (W)
    """
    # 유리를 통한 직접 투과 일사량
    Q_direct = glass_transmittance * solar_irradiance * glass_area

    # 집열판에서의 일사 흡수량 (5.2 공식의 α × Isol 개념)
    Q_collector = collector_absorptance * glass_transmittance * solar_irradiance * collector_area

    return Q_direct + Q_collector
