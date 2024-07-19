import requests


def get_settings() -> dict[str]:
    settings_url = 'http://127.0.0.1:8000/settings'
    try:
        req = requests.get(settings_url)
        return req.json()
    except Exception:
        return


def send_stat(stat_type: str):
    stat_url = 'http://127.0.0.1:8000/bot-stats'
    data = {stat_type: True}
    try:
        requests.post(stat_url, data)
    except Exception:
        return
