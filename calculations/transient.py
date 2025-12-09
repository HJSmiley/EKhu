"""
비정상 열전도 해석 모듈 (Transient Thermal Analysis using RC Model)

이 모듈은 건축물의 비정상 열전도 해석을 위한 함수들을 제공합니다.
- 1R1C 모델 기반 온도 계산 (5.1 공식)
- 이산화된 열평형 계산 (5.2 공식)
"""

from typing import List, Tuple


def simulate_transient_response(
    initial_temp: float,
    outdoor_temps: List[float],
    solar_gains: List[float],
    heating_inputs: List[float],
    thermal_resistance: float,
    thermal_capacity: float,
    timestep: float,
    use_implicit: bool = True
) -> Tuple[List[float], List[float]]:
    """
    여러 시간단계에 걸친 비정상 열응답을 시뮬레이션합니다. (5.1, 5.2 공식)

    1R1C 모델 (5.1 공식)과 이산화된 열평형 (5.2 공식)을 기반으로
    시간에 따른 실내온도 변화를 계산합니다.

    매개변수:
        initial_temp: 초기 실내온도 (°C)
        outdoor_temps: 외기온도 리스트 (°C)
        solar_gains: 일사 획득량 리스트 (W)
        heating_inputs: 난방 입력 리스트 (W)
        thermal_resistance: 열저항 R (K/W)
        thermal_capacity: 열용량 C (J/K)
        timestep: 시간간격 dt (s)
        use_implicit: 암시적(True) 또는 명시적(False) 적분법 선택

    반환값:
        (실내온도 리스트, 난방부하 리스트) 튜플
    """
    n_steps = len(outdoor_temps)
    indoor_temps = [initial_temp]
    heating_loads = []

    T_current = initial_temp

    for i in range(n_steps):
        T_outdoor = outdoor_temps[i]
        Q_solar = solar_gains[i]
        Q_heating = heating_inputs[i]

        # 다음 시간단계 온도 계산 (5.2 공식 - 암시적 방법)
        # 암시적 스킴 계수: α = dt / (C × R)
        alpha = timestep / (thermal_capacity * thermal_resistance)
        
        # 풀이: T_new = (T_old + α × (Te + R × (Φ + Qsolar))) / (1 + α)
        numerator = T_current + alpha * (T_outdoor + thermal_resistance * (Q_heating + Q_solar))
        denominator = 1 + alpha
        T_next = numerator / denominator

        # 필요 난방부하 계산: Q_loss = (Ti - Te) / R
        Q_loss = (T_current - T_outdoor) / thermal_resistance
        Q_load = Q_loss - Q_solar

        indoor_temps.append(T_next)
        heating_loads.append(Q_load)

        T_current = T_next

    return indoor_temps, heating_loads


def estimate_thermal_capacity(
    building_volume: float,
    wall_thickness: float = 0.3,
    density: float = 1800.0,
    specific_heat: float = 1000.0
) -> float:
    """
    건물 체적과 재료 물성으로부터 열용량을 추정합니다. (5.1 공식 관련)

    열용량 공식: C = m × cp = ρ × V × cp

    1R1C 모델 (5.1 공식)에서 사용되는 열용량 C를 추정합니다.

    매개변수:
        building_volume: 건물 체적 (m³)
        wall_thickness: 평균 벽 두께 (m, 기본값 0.3)
        density: 재료 밀도 ρ (kg/m³, 기본값 1800.0)
        specific_heat: 비열 cp (J/kg·K, 기본값 1000.0)

    반환값:
        열용량 C (J/K)
    """
    # 건물 외피 질량 추정
    # 정육면체 가정 시 표면적 ≈ 6 × 체적^(2/3)
    surface_area = 6.0 * (building_volume ** (2.0 / 3.0))
    mass = surface_area * wall_thickness * density

    # 열용량 = 질량 × 비열
    return mass * specific_heat


def estimate_thermal_resistance(
    wall_area: float,
    wall_u_value: float,
    roof_area: float,
    roof_u_value: float,
    floor_area: float,
    floor_u_value: float,
    window_area: float,
    window_u_value: float
) -> float:
    """
    건물 부위별 열저항으로부터 총 열저항을 추정합니다. (1.2 공식 관련)

    병렬 열저항 공식: 1/R_total = Σ(A_i × U_i) = D_tot

    열관류량 (1.2 공식): D = (1/Rt) × A
    따라서 총 열저항: R_total = 1 / Σ(A_i × U_i)

    매개변수:
        wall_area: 벽체 면적 (m²)
        wall_u_value: 벽체 열관류율 U (W/m²·K)
        roof_area: 지붕 면적 (m²)
        roof_u_value: 지붕 열관류율 U (W/m²·K)
        floor_area: 바닥 면적 (m²)
        floor_u_value: 바닥 열관류율 U (W/m²·K)
        window_area: 창문 면적 (m²)
        window_u_value: 창문 열관류율 U (W/m²·K)

    반환값:
        총 열저항 R (K/W)
    """
    # 총 열관류량 (열전도도): D_tot = Σ(A_i × U_i) (1.2 공식)
    total_conductance = (
        wall_area * wall_u_value +
        roof_area * roof_u_value +
        floor_area * floor_u_value +
        window_area * window_u_value
    )

    # 총 열저항: R = 1 / D_tot
    if total_conductance > 0:
        return 1.0 / total_conductance
    else:
        return float('inf')
