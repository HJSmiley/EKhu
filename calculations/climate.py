# 위도/경도 기반 온도 및 일사량 조회 - Open-Meteo API 사용 (무료, API 키 불필요)
# 당일 현재 시간까지: 관측 데이터 / 당일 현재 시간 이후: 예측 데이터

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional


def calculate_sky_temperature(
    outdoor_temp: float,
    cloud_cover: float = 0.0,
    relative_humidity: float = 0.5
) -> float:
    """
    장파복사를 위한 유효 하늘 온도를 계산합니다. (4.1 공식 관련)

    매개변수:
        outdoor_temp: 외기온도 (°C)
        cloud_cover: 운량 (0-1)
        relative_humidity: 상대습도 (0-1)

    반환값:
        하늘 온도 T_sky (°C)
    """
    clear_sky_depression = 6.0 * (1.0 - relative_humidity * 0.5)
    effective_depression = clear_sky_depression * (1.0 - cloud_cover * 0.8)
    return outdoor_temp - effective_depression


def get_weather_from_api(lat: float, lon: float) -> Optional[Dict]:
    """
    위도/경도로 오늘 00시부터 다음날 00시까지(25시간)의 온도와 일사량을 가져옵니다.
    현재 시간까지는 관측 데이터, 이후는 예측 데이터입니다.

    Args:
        lat: 위도
        lon: 경도

    Returns:
        시간별 날씨 데이터 딕셔너리 또는 None (실패 시)
    """
    try:
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")
        current_hour = now.hour

        hourly_vars = [
            "temperature_2m",           # 기온 (°C)
            "relative_humidity_2m",     # 상대습도 (%)
            "direct_radiation",         # 직달일사량 (W/m²)
            "diffuse_radiation",        # 산란일사량 (W/m²)
            "shortwave_radiation",      # 전일사량 (W/m²)
            "cloud_cover",              # 운량 (%)
        ]

        # 1. 과거 관측 데이터 가져오기 (00시 ~ 현재시간)
        archive_url = "https://archive-api.open-meteo.com/v1/archive"
        archive_params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": ",".join(hourly_vars),
            "start_date": today,
            "end_date": today,
            "timezone": "Asia/Seoul"
        }

        archive_response = requests.get(archive_url, params=archive_params, timeout=10)
        archive_response.raise_for_status()
        archive_data = archive_response.json()

        # 2. 예측 데이터 가져오기 (오늘 ~ 내일, 다음날 00시 포함)
        forecast_url = "https://api.open-meteo.com/v1/forecast"
        forecast_params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": ",".join(hourly_vars),
            "start_date": today,
            "end_date": tomorrow,
            "timezone": "Asia/Seoul"
        }

        forecast_response = requests.get(forecast_url, params=forecast_params, timeout=10)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

        # 3. 데이터 합치기: 00시~현재시간은 관측, 이후~다음날 00시는 예측
        combined_hourly = {}
        archive_hourly = archive_data.get("hourly", {})
        forecast_hourly = forecast_data.get("hourly", {})

        for var in ["time"] + hourly_vars:
            archive_values = archive_hourly.get(var, [])
            forecast_values = forecast_hourly.get(var, [])

            # 현재 시간까지는 관측 데이터, 이후는 예측 데이터 (25시간: 오늘 00시 ~ 내일 00시)
            combined = []
            for i in range(25):
                if i <= current_hour and i < len(archive_values):
                    combined.append(archive_values[i])
                elif i < len(forecast_values):
                    combined.append(forecast_values[i])
                else:
                    combined.append(None)
            combined_hourly[var] = combined

        return {
            "hourly": combined_hourly,
            "current_hour": current_hour,
            "observation_hours": list(range(0, current_hour + 1)),
            "forecast_hours": list(range(current_hour + 1, 25))
        }

    except Exception as e:
        print(f"Weather API 오류: {e}")
        return None


def generate_hourly_climate_data(latitude: float, longitude: float) -> List[Dict]:
    """
    위치 기반 25시간(오늘 00시 ~ 내일 00시) 기후 데이터를 생성합니다.
    현재 시간까지는 관측 데이터, 이후는 예측 데이터입니다.

    Args:
        latitude: 위도
        longitude: 경도

    Returns:
        시간별 기후 데이터 리스트 (25시간)
    """
    api_data = get_weather_from_api(latitude, longitude)

    if not api_data:
        raise Exception("날씨 API 호출 실패")

    hourly = api_data.get("hourly", {})
    current_hour = api_data.get("current_hour", 0)
    temps = hourly.get("temperature_2m", [])
    humidity = hourly.get("relative_humidity_2m", [])
    direct_rad = hourly.get("direct_radiation", [])
    diffuse_rad = hourly.get("diffuse_radiation", [])
    shortwave_rad = hourly.get("shortwave_radiation", [])
    cloud = hourly.get("cloud_cover", [])

    climate_data = []
    for hour in range(min(25, len(temps))):
        outdoor_temp = temps[hour] if temps[hour] is not None else 0.0
        solar_radiation = shortwave_rad[hour] if shortwave_rad[hour] is not None else 0.0
        humidity_val = humidity[hour] if humidity and humidity[hour] is not None else 50.0
        cloud_val = cloud[hour] if cloud and cloud[hour] is not None else 0.0

        sky_temp = calculate_sky_temperature(
            outdoor_temp,
            cloud_cover=cloud_val / 100,      # API는 0-100%, 함수는 0-1
            relative_humidity=humidity_val / 100
        )

        # 관측/예측 구분
        data_type = "observation" if hour <= current_hour else "forecast"

        climate_data.append({
            'hour': hour,
            'outdoor_temp': outdoor_temp,
            'solar_radiation': solar_radiation,
            'sky_temp': sky_temp,
            'humidity': humidity_val,
            'direct_radiation': direct_rad[hour] if direct_rad and direct_rad[hour] is not None else 0.0,
            'diffuse_radiation': diffuse_rad[hour] if diffuse_rad and diffuse_rad[hour] is not None else 0.0,
            'cloud_cover': cloud_val,
            'data_type': data_type,
        })

    return climate_data
