import time
import random

from logging_settings import logger, LogFolderPath
from fake_headers import Headers
from headbot_data import send_stat, get_settings

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
# Settings
settings = get_settings()

# Driver
DRIVER_PATH_CONF = settings['driver_path']

# Path to log folder
LogFolderPath.path = 'logs/'

# URLs
URLS = settings['urls']

# Scrolls
SCROLL_DELAY_MIN: float = random.uniform(0.25, 1)
SCROLL_DELAY_MAX: float = random.uniform(1, 1.75)
SCROLL_STEP_MIN: int = random.randint(5, 15)
SCROLL_STEP_MAX: int = random.randint(15, 45)

# Delay
DELAY_ON_PAGE: float = random.uniform(1, 3)

# Counts
RANDOM_PAGE_COUNTS: int =  random.randint(3, 5)

logger.info('Service Start')


@logger.catch
def get_random_headers() -> dict:
    headers: dict[str] = Headers(headers=True).generate()
    return headers


@logger.catch
def set_random_headers(driver, headers) -> None:
    logger.info(f'Setting random Headers: {headers}')
    driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {'headers': headers})

@logger.catch
def get_random_user_agents() -> str:
    ua = get_random_headers()['User-Agent']
    return ua


@logger.catch
def get_random_chrome_options() -> webdriver.ChromeOptions:
    options: webdriver.ChromeOptions = webdriver.ChromeOptions()

    prefs: dict[str] = {
        "profile.default_content_setting_values.notifications": 1,
    }
    options.add_experimental_option("prefs", prefs)

    # options.add_argument("--incognito")

    # Headless - backgorund mode without GUI
    options.add_argument("--headless")

    options.add_argument('--no-sandbox')
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(
        f"--window-size={random.randint(800, 1920)},{random.randint(600, 1080)}")
    logger.info('Returning Chrome options for Driver and random window size')
    return options

@logger.catch
def smooth_scroll(driver: webdriver.Chrome) -> None:
    driver.implicitly_wait(random.randint(2, 6))
    page_height = driver.execute_script("return document.body.scrollHeight")
    window_height = driver.execute_script("return window.innerHeight")

    if page_height <= window_height:
        logger.info(f"No need to scroll, the page height is within the window height. {driver.current_url}")
        return

    current_position = 0
    end_position = random.randint(150, 1500)
    scroll_step = random.randint(SCROLL_STEP_MIN, SCROLL_STEP_MAX)

    while current_position < end_position:
        logger.info(f'Current postion: {current_position} - End position: {end_position}  site: {driver.current_url}')
        current_position += scroll_step
        driver.execute_script(f"window.scrollTo(0, {current_position});")
        scroll_step = random.randint(SCROLL_STEP_MIN, SCROLL_STEP_MAX)
        time.sleep(random.uniform(SCROLL_DELAY_MIN, SCROLL_DELAY_MAX))


@logger.catch
def scroll_to_element(driver: webdriver.Chrome, element: str) -> None:
    logger(f'Scrolling to the element')
    driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", element)
    time.sleep(random.uniform(SCROLL_DELAY_MIN, SCROLL_DELAY_MAX))


@logger.catch
def get_random_link(link: list) -> str:
    random.shuffle(link)
    r_link: str = random.choice(link)
    href: str = r_link.get_attribute('href')
    logger.info(f'Random link {href}')
    return r_link

@logger.catch
def find_all_links(driver: webdriver.Chrome) -> list:
    return driver.find_elements(By.TAG_NAME, 'a')

@logger.catch
def click_random_links(driver: webdriver.Chrome, url) -> None:
    logger.info(f'All links on page {len(find_all_links(driver))}')
    random_link: str = get_random_link(find_all_links(driver))
    time.sleep(4)

    try:
        driver.execute_script('arguments[0].click();', random_link)
        logger.info('Execute click!')
        send_stat('links', driver.current_url)
        time.sleep(DELAY_ON_PAGE)
    except (selenium.common.exceptions.ElementNotInteractableException, selenium.common.exceptions.ElementClickInterceptedException, Exception) as ex:
        logger.info('Execute get method')
        logger.error(f'Error on click to random link {ex}')
        driver.get(get_random_link(find_all_links(driver)).get_attribute('href'))
        send_stat('links', driver.current_url)
        time.sleep(DELAY_ON_PAGE)

    except AttributeError as ex:
        logger.error(f'Error while click non page, turning back {ex}')
        time.sleep(random.randint(2, 7))

    smooth_scroll(driver)

    time.sleep(DELAY_ON_PAGE)
    
    for _ in range(RANDOM_PAGE_COUNTS):
        logger.info(f"Random page current count: {_} \n Page: {driver.current_url}")
        driver.execute_script('arguments[0].click();', get_random_link(find_all_links(driver)))
        time.sleep(DELAY_ON_PAGE)
        smooth_scroll(driver)
        send_stat('links', driver.current_url)
    
    time.sleep(DELAY_ON_PAGE)

@logger.catch
def main(url: str) -> None:
    logger.info(f'Starting main function kwargs')
    options: str = get_random_chrome_options()
    headers: dict[str] = get_random_headers()

    driver_path: str = DRIVER_PATH_CONF
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(options=options, service=service)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("""Object.defineProperty(navigator, 'userAgent', {get: () => arguments[0]})""", get_random_user_agents())
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": get_random_user_agents(),"platform": "Windows"})
    set_random_headers(driver, headers)

    try:
        logger.info(f'Request to the url: {url}')
        driver.get(url)


        # Waiting to all of page components
        driver.implicitly_wait(random.randint(4, 8))

        logger.info('Started smooth scrolling')

        smooth_scroll(driver)
        
        time.sleep(DELAY_ON_PAGE)

        logger.info(f'Going to the random pages {url}')
        click_random_links(driver, url)
        logger.info(f"Cookies: {driver.get_cookies()}")
        time.sleep(random.randint(2, 7))

    except Exception as e:
        logger.error(f'Error on main function {e} {driver.current_url}')
    finally:
        try:
            time.sleep(DELAY_ON_PAGE)
            driver.delete_all_cookies()
            logger.info('Deleting cookies')
            send_stat('interval')
            logger.success(f'Quiting the driver {driver.current_url}')
            driver.close()
            driver.quit()
        except Exception as e:
            import sys
            logger.error(f'Error while quiting the driver {e} {driver.current_url}')
            sys.exit()


if __name__ == "__main__":
    from multiprocessing import Process
    logger.success(f'Urls: {URLS}')

    try:
        procceses = []
        for url in URLS:
            procces = Process(target=main, args=(url,))
            procceses.append(procces)
            procces.start()
            
        for pro in procceses:
             pro.join()
    except KeyboardInterrupt as ex:
        pass