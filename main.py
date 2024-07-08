import time
import random
import configparser

from logging_settings import logger, LogFolderPath
from fake_headers import Headers

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By

# Conf
conf = configparser.ConfigParser()
conf.read('settings.ini')

# Driver
DRIVER_PATH_CONF = conf['Driver']['path']

# Path to log folder
LogFolderPath.path = conf['LOGS']['path']

# URLs
URLS = conf['URLs']['urls'].split(',')

# Scrolls
SCROLL_DELAY_MIN: float = float(conf['Timers']['scroll_delay_min'])
SCROLL_DELAY_MAX: float = float(conf['Timers']['scroll_delay_max'])
SCROLL_STEP_MIN: int = int(conf['Counts']['scroll_step_min'])
SCROLL_STEP_MAX: int = int(conf['Counts']['scroll_step_max'])

# Delay
DELAY_ON_PAGE: float = float(conf['Timers']['delay_on_page'])

# Counts
RANDOM_PAGE_COUNTS: int = int(conf['Counts']['random_page_counts'])

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
def manage_cookies(driver: webdriver.Chrome) -> None:
    driver.implicitly_wait(2)
    logger.info('Managing cookies')
    try:
        cookies: dict[str] = driver.get_cookies()
        if cookies:
            for cookie in cookies:
                if random.choice([True, False]):
                    driver.delete_cookie(cookie['name'])
                else:
                    new_expiry = cookie.get('expiry', int(
                        time.time()) + random.randint(3600, 7200))
                    driver.add_cookie({
                        'name': cookie['name'],
                        'value': cookie['value'],
                        'domain': cookie['domain'],
                        'path': cookie['path'],
                        'expiry': new_expiry,
                        'secure': cookie.get('secure', False),
                        'httpOnly': cookie.get('httpOnly', False),
                        'sameSite': cookie.get('sameSite', 'None'),
                    })
            logger.success('Cookies done!')
    except Exception as e:
        logger.error(f'Cookies error! {e}')


@logger.catch
def smooth_scroll(driver: webdriver.Chrome) -> None:
    driver.implicitly_wait(5)
    page_height = driver.execute_script("return document.body.scrollHeight")
    window_height = driver.execute_script("return window.innerHeight")

    if page_height <= window_height:
        logger.info("No need to scroll, the page height is within the window height.")
        return

    current_position = 0
    end_position = random.randint(150, 500)
    scroll_step = random.randint(SCROLL_STEP_MIN, SCROLL_STEP_MAX)

    while current_position < end_position:
        logger.info(f'Current postion: {current_position} - End position: {end_position}')
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
    r_link: str = random.choice(link)
    href: str = r_link.get_attribute('href')
    logger.info(f'Random link {href}')
    return r_link


@logger.catch
def click_random_links(driver: webdriver.Chrome) -> None:
    links: list = driver.find_elements(By.TAG_NAME, 'a')
    logger.info(f'All links on page {len(links)}')
    random_link: str = get_random_link(links)
    time.sleep(4)

    try:
        random_link.click()
        time.sleep(DELAY_ON_PAGE)
    except selenium.common.exceptions.ElementNotInteractableException as ex:
        logger.error(f'Error on click to random link {ex}')
        get_random_link(links).click()
        time.sleep(DELAY_ON_PAGE)

    except AttributeError as ex:
        logger.error(f'Error while click non page, turning back {ex}')
        time.sleep(4)
        driver.back()

    smooth_scroll(driver)

    time.sleep(DELAY_ON_PAGE)
    driver.back()
    logger.success('Back to the main page')


@logger.catch
def main(url: str) -> None:
    logger.info(f'Starting main function kwargs')
    options: str = get_random_chrome_options()
    headers: dict[str] = get_random_headers()

    driver_path: str = DRIVER_PATH_CONF
    driver = webdriver.Chrome(options=options, executable_path=driver_path)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("""Object.defineProperty(navigator, 'userAgent', {get: () => arguments[0]})""", get_random_user_agents())
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": get_random_user_agents(),"platform": "Windows"})
    set_random_headers(driver, headers)

    try:
        logger.info(f'Request to the url: {url}')
        driver.get(url)


        # Waiting to all of page components
        driver.implicitly_wait(10)

        manage_cookies(driver)

        logger.info('Started smooth scrolling')

        smooth_scroll(driver)
        
        time.sleep(DELAY_ON_PAGE)

        logger.info('Going to the random pages')
        for c in range(RANDOM_PAGE_COUNTS):
            if c <= RANDOM_PAGE_COUNTS:
                logger.info('Going to the next page')
                click_random_links(driver)
            time.sleep(5)

    except Exception as e:
        logger.error(f'Error on main function {e}')
    finally:
        try:
            time.sleep(DELAY_ON_PAGE)
            driver.quit()
            logger.success('Quiting the driver')
        except Exception as e:
            logger.error(f'Error while quiting the driver {e}')
            import sys
            sys.exit()


if __name__ == "__main__":
    import threading
    logger.success(f'Urls: {URLS}')

    try:
        for url in URLS:
            threading.Thread(target=main, args=(url,)).start()
    except KeyboardInterrupt as ex:
        pass
