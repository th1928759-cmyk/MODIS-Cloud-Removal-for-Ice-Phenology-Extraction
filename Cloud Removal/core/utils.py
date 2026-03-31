import datetime

def get_ice_season_dates(year):
    """
    定义冰物候年：从当年11月1日开始的242天
    平年止于次年6月30日，闰年止于次年6月29日
    """
    start_date = datetime.date(year, 11, 1)
    return [start_date + datetime.timedelta(days=i) for i in range(242)]

def get_priority_value(month, ice_val, water_val):
    """
    获取月份判别优先级：1-4月优先为冰，其余优先为水
    """
    return ice_val if 1 <= month <= 4 else water_val
