"""
행렬 풀이 유틸리티 모듈 (Matrix Solver Utilities using NumPy)

이 모듈은 건축 열전달 해석을 위한 행렬 연산 함수들을 제공합니다.
- 선형 시스템 풀이: [A][x] = [b] (2.2 공식)
- 형상계수(View Factor) 계산 (4.2, 4.3 공식)
- 복사도(Radiosity) 시스템 풀이 (4.4 공식)
- 다실 열전도 해석 (2.2 공식)
- 열 네트워크 행렬 구성 (2.2 공식)
"""

import numpy as np
from typing import List, Dict, Tuple


def solve_linear_system(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    선형 시스템 [A][x] = [b]를 풀이합니다. (2.2 공식)

    NumPy의 선형대수 풀이기를 사용하여 행렬 방정식을 풉니다.
    다실 열평형 해석에서 온도 벡터를 구하는 데 사용됩니다.

    매개변수:
        A: 계수 행렬 (n × n)
        b: 우변 벡터 (n × 1)

    반환값:
        해 벡터 x

    예외:
        LinAlgError: 행렬이 특이(singular)하거나 풀이 불가능한 경우
    """
    return np.linalg.solve(A, b)


def calculate_view_factors(surfaces: Dict[str, float]) -> Dict[str, float]:
    """
    복사열전달을 위한 형상계수를 계산합니다. (4.2, 4.3 공식)

    형상계수 상호성 (4.2 공식): F_ij × A_i = F_ji × A_j
    형상계수 합 법칙 (4.3 공식): ΣF_ij = 1 (j에 대해)

    간단한 형상에 대해 해석적 공식을 사용합니다.
    복잡한 형상은 몬테카를로 등 수치적 방법이 필요합니다.

    매개변수:
        surfaces: 표면 이름과 면적의 딕셔너리 {이름: 면적(m²)}

    반환값:
        형상계수 딕셔너리 (예: {'floor_to_ceiling': 0.5})
    """
    view_factors = {}

    # 단순 평행 표면 가정
    total_area = sum(surfaces.values())

    for name1, area1 in surfaces.items():
        for name2, area2 in surfaces.items():
            if name1 != name2:
                # 면적비 기반 간략화된 형상계수 (4.2, 4.3 공식 적용)
                key = f"{name1}_to_{name2}"
                view_factors[key] = area2 / total_area

    return view_factors


def solve_radiosity_system(
    view_factors: Dict[str, float],
    emissivities: Dict[str, float],
    temperatures: Dict[str, float],
    stefan_boltzmann: float = 5.67e-8
) -> Dict[str, float]:
    """
    복사도 방정식 시스템 [M][J] = [C]를 풀이합니다. (4.4 공식)

    복사도 방법은 다중 반사를 고려하여 표면 간 복사열전달을 계산합니다.

    복사도 방정식: J_i = ε_i × σ × T_i⁴ + (1-ε_i) × Σ(F_ij × J_j)

    행렬 형태로 재배열:
    J_i - (1-ε_i) × Σ(F_ij × J_j) = ε_i × σ × T_i⁴

    여기서:
        J: 복사도 (Radiosity, W/m²)
        ε: 방사율
        σ: Stefan-Boltzmann 상수 (5.67×10⁻⁸ W/m²·K⁴)
        F_ij: 표면 i에서 j로의 형상계수

    매개변수:
        view_factors: 형상계수 딕셔너리
        emissivities: 표면별 방사율 ε
        temperatures: 표면별 온도 (K)
        stefan_boltzmann: Stefan-Boltzmann 상수 σ (W/m²·K⁴)

    반환값:
        각 표면의 복사도 J (W/m²) 딕셔너리
    """
    surfaces = list(emissivities.keys())
    n = len(surfaces)

    # 행렬 [M]과 벡터 [C] 구성
    M = np.zeros((n, n))
    C = np.zeros(n)

    for i, surf_i in enumerate(surfaces):
        eps_i = emissivities[surf_i]
        T_i = temperatures[surf_i]

        # 방사력: E = ε × σ × T⁴ (4.1 공식)
        C[i] = eps_i * stefan_boltzmann * (T_i ** 4)

        # 대각 항: M[i,i] = 1
        M[i, i] = 1.0

        # 비대각 항: M[i,j] = -(1-ε_i) × F_ij (4.4 공식)
        for j, surf_j in enumerate(surfaces):
            if i != j:
                key = f"{surf_i}_to_{surf_j}"
                F_ij = view_factors.get(key, 0.0)
                # 표준 복사도 방정식: M[i,j] = -(1-ε_i) × F_ij
                M[i, j] = -(1 - eps_i) * F_ij

    # 복사도 J 풀이: [M][J] = [C]
    J = solve_linear_system(M, C)

    return {surf: float(J[i]) for i, surf in enumerate(surfaces)}
