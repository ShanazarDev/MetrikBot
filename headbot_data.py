import requests


def get_settings() -> dict[str]:
    settings_url = 'http://192.168.0.252:8045/settings'
    try:
        req = requests.get(settings_url)
        return req.json()
    except Exception:
        return


def send_stat(stat_type: str):
    stat_url = 'http://192.168.0.252:8045/bot-stats'
    data = {stat_type: True}
    try:
        requests.post(stat_url, data)
    except Exception:
        return
