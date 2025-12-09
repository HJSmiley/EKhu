"""Open-Meteo API를 사용한 기후 데이터 생성 모듈"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from calculations.solar import calculate_sky_temperature


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
            "current_hour": current_hour
        }
    
    except Exception as e:
        print(f"Weather API 오류: {e}")
        return None


def generate_hourly_climate_data(latitude: float, longitude: float) -> List[Dict]:
    """
    위치 기반 25시간(오늘 00시 ~ 내일 00시) 기후 데이터를 생성합니다.

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
    temps = hourly.get("temperature_2m", [])
    humidity = hourly.get("relative_humidity_2m", [])
    direct_rad = hourly.get("direct_radiation", [])
    diffuse_rad = hourly.get("diffuse_radiation", [])
    shortwave_rad = hourly.get("shortwave_radiation", [])

    climate_data = []
    for hour in range(min(25, len(temps))):
        outdoor_temp = temps[hour] if temps[hour] is not None else 0.0
        solar_radiation = shortwave_rad[hour] if shortwave_rad[hour] is not None else 0.0
        sky_temp = calculate_sky_temperature(outdoor_temp)

        climate_data.append({
            'hour': hour,
            'outdoor_temp': outdoor_temp,
            'solar_radiation': solar_radiation,
            'sky_temp': sky_temp,
            'humidity': humidity[hour] if humidity and humidity[hour] is not None else 50.0,
            'direct_radiation': direct_rad[hour] if direct_rad and direct_rad[hour] is not None else 0.0,
            'diffuse_radiation': diffuse_rad[hour] if diffuse_rad and diffuse_rad[hour] is not None else 0.0,
        })

    return climate_data