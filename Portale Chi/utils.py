from datetime import date, timedelta

def get_today():
    return date.today()

def get_ayear_later(today):
    return today + timedelta(days=365)