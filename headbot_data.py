import requests
import aiohttp

def get_settings() -> dict[str]:
    settings_url = 'http://192.168.0.252:8045/settings/'
    try:
        req = requests.get(settings_url)
        return req.json()
    except Exception:
        pass
    
def get_proxy() -> dict[str]:
    proxy_url = 'http://192.168.0.252:8045/proxy/'
    try:
        req = requests.get(proxy_url)
        return req.json()
    except Exception:
        pass

async def send_stat(stat_type: str, url: str=None):
    stat_url = 'http://192.168.0.252:8045/bot-stats/'
    data = {stat_type: url if url is not None else True}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(stat_url, data=data) as response:
                # Проверка успешности запроса
                if response.status == 200:
                    print("Статус успешно отправлен")
                else:
                    print(f"Ошибка при отправке статуса: {response.status}")
    except Exception as e:
        pass

