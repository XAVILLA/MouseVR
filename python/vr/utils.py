from datetime import date

def get_date():
    """
    Returns today's date in 'yyyymmdd' format as a string
    str :return: today's date
    """
    today = date.today()
    return today.strftime("%Y%m%d")