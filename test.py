from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options


def setup_driver_with_profile(profile_path=None):
    chrome_options = Options()
    chrome_options.add_argument('add_experimental_option("excludeSwitches",["ignore-certificate-errors"])')

    proxy = {
        'connection_type': 'https',
        # Дополнительные параметры для настройки HTTPS-соединения
        'verify_ssl': False,  # Отключение проверки SSL-сертификата
        # Указание конкретного шифра
        'ssl_insecure_cipher_suites': ['TLS_RSA_WITH_AES_256_CBC_SHA'],
        'proxy': {
            "https": "https://nixdatacomm:MiaeZXxgHT@166.1.12.170:51523",
        }
    }

    driver = webdriver.Chrome(options=chrome_options, seleniumwire_options=proxy)
    return driver


if __name__ == '__main__':
    driver = setup_driver_with_profile()

    driver.get('https://turkmenportal.com')
    print(driver.page_source)
    driver.quit()
