import math
import re
from datetime import datetime
import requests

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    计算两个经纬度点之间的距离（米）
    使用Haversine公式
    """
    # 将经纬度转换为弧度
    lat1_rad = math.radians(float(lat1))
    lon1_rad = math.radians(float(lon1))
    lat2_rad = math.radians(float(lat2))
    lon2_rad = math.radians(float(lon2))
    
    # Haversine公式
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # 地球半径（米）
    r = 6371000
    
    return c * r

def parse_location_string(location_str):
    """
    解析位置字符串，提取经纬度
    格式: "latitude,longitude (address)"
    """
    try:
        # 提取经纬度部分
        coords_part = location_str.split(' (')[0]
        lat_str, lon_str = coords_part.split(',')
        return float(lat_str), float(lon_str)
    except:
        return None, None

def is_within_range(lat1, lon1, location_str, distance_threshold):
    """检查是否在指定范围内"""
    try:
        # 解析位置字符串
        if not location_str or ',' not in location_str:
            return True  # 如果没有设置位置，默认允许打卡
        
        lat2_str, lon2_str = location_str.split(',')[0], location_str.split(',')[1]
        lon2_str = lon2_str.split('(')[0].strip()
        
        lat2 = float(lat2_str.strip())
        lon2 = float(lon2_str.strip())
        
        # 计算距离（使用Haversine公式）
        R = 6371000  # 地球半径（米）
        
        lat1_rad = math.radians(float(lat1))
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - float(lat1))
        delta_lon = math.radians(lon2 - float(lon1))
        
        a = math.sin(delta_lat/2) * math.sin(delta_lat/2) + \
            math.cos(lat1_rad) * math.cos(lat2_rad) * \
            math.sin(delta_lon/2) * math.sin(delta_lon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance <= distance_threshold
        
    except Exception as e:
        print(f"距离计算错误: {e}")
        return True  # 出错时默认允许打卡

def validate_phone(phone):
    """验证手机号格式"""
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))

def validate_password(password):
    """验证密码强度"""
    if len(password) < 6:
        return False, "密码长度至少6位"
    
    if not re.search(r'[a-zA-Z]', password):
        return False, "密码必须包含字母"
    
    if not re.search(r'\d', password):
        return False, "密码必须包含数字"
    
    return True, "密码格式正确"

def format_time(time_str):
    """格式化时间字符串"""
    if not time_str:
        return None
    
    try:
        # 如果是datetime对象，转换为字符串
        if isinstance(time_str, datetime):
            return time_str.strftime('%H:%M')
        
        # 如果是字符串，尝试解析
        if isinstance(time_str, str):
            # 处理不同的时间格式
            if ':' in time_str:
                # 已经是HH:MM格式
                return time_str
            elif 'T' in time_str:
                # ISO格式
                dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                return dt.strftime('%H:%M')
            else:
                # 尝试解析其他格式
                dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                return dt.strftime('%H:%M')
    except Exception as e:
        print(f"时间格式化错误: {e}")
        return None

def parse_time(time_str):
    """解析时间字符串为datetime对象"""
    if not time_str:
        return None
    
    try:
        if isinstance(time_str, datetime):
            return time_str
        
        if isinstance(time_str, str):
            if ':' in time_str and len(time_str) == 5:
                # HH:MM格式
                return datetime.strptime(time_str, '%H:%M').time()
            elif 'T' in time_str:
                # ISO格式
                return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            else:
                # 其他格式
                return datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"时间解析错误: {e}")
        return None 
    
def format_location_display(location_str):
    """格式化位置显示，遇到纯经纬度时自动调用高德地图API获取详细地址"""
    if not location_str:
        return '未知位置'
    # 如果已经是格式化的地址（包含括号），直接返回
    if ' (' in location_str and location_str.endswith(')'):
        return location_str
    # 如果是纯经纬度格式，尝试转换为地址
    if ',' in location_str and '(' not in location_str:
        try:
            coords = location_str.split(',')
            if len(coords) == 2:
                lat = float(coords[0].strip())
                lng = float(coords[1].strip())
                # 调用高德地图API获取详细地址
                address = get_address_from_coords(lat, lng)
                return f"{lat:.2f}, {lng:.2f} ({address})"
        except:
            pass
    return location_str

def get_address_from_coords(lat, lng):
    """调用高德地图API获取详细地址"""
    try:
        # 当前Key为JS API Key，无法用于Web服务API
        api_key = "5c3066c36f6fa333afc7f55f78c33ff0"  # 需要替换为实际的Web服务API Key
        
        # API Key已配置，继续调用高德API
        
        url = "https://restapi.amap.com/v3/geocode/regeo"
        params = {
            "key": api_key,
            "location": f"{lng},{lat}",  # 高德API格式：经度,纬度
            "poitype": "",
            "radius": 1000,
            "extensions": "all",
            "batch": "false",
            "roadlevel": 0
        }
        
        resp = requests.get(url, params=params, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"高德API响应: {data}")  # 调试信息
            if data.get("status") == "1" and data.get("regeocode"):
                regeocode = data["regeocode"]
                formatted_address = regeocode.get("formatted_address", "")
                if formatted_address:
                    return formatted_address
                # 如果没有formatted_address，尝试组合地址
                address_component = regeocode.get("addressComponent", {})
                province = address_component.get("province", "")
                city = address_component.get("city", "")
                district = address_component.get("district", "")
                township = address_component.get("township", "")
                street = address_component.get("streetNumber", {}).get("street", "")
                number = address_component.get("streetNumber", {}).get("number", "")
                
                address_parts = [province, city, district, township, street, number]
                combined_address = "".join([part for part in address_parts if part])
                return combined_address if combined_address else f"经纬度: {lat:.6f}, {lng:.6f}"
            else:
                print(f"高德API错误: {data.get('info', '未知错误')}")
                return f"经纬度: {lat:.6f}, {lng:.6f}"
        return f"经纬度: {lat:.6f}, {lng:.6f}"
    except Exception as e:
        print("高德逆地理编码失败:", e)
        return f"经纬度: {lat:.6f}, {lng:.6f}"