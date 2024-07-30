import time, random, asyncio

from logging_settings import logger
from headbot_data import send_stat, get_settings, get_proxy

from fake_headers import Headers
from urllib.parse import urlparse

import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumwire import webdriver


class AdBot:
     
     settings = get_settings()
     url_from_api = settings['urls']
     
     @logger.catch
     def __init__(self, url: str) -> None:
        self.url = url

        # Settings
        self.url_from_api = self.settings['urls']

        # Driver path
        self.DRIVER_PATH = self.settings['driver_path']
        
        # Scrolls
        self.SCROLL_DELAY_MIN: float = random.uniform(0.25, 1)
        self.SCROLL_DELAY_MAX: float = random.uniform(1, 1.75)
        self.SCROLL_STEP_MIN: int = random.randint(5, 15)
        self.SCROLL_STEP_MAX: int = random.randint(15, 45)

        # Delay
        self.DELAY_ON_PAGE: float = random.uniform(1, 3)

        # Counts
        self.RANDOM_PAGE_COUNTS: int = random.randint(2, 4)

        
        # Proxy
        self.proxy: dict[str] = get_proxy()['proxy']
        self.proxy_options: dict[str] = {
             "proxy": {
               "http": f"{self.proxy['protocol']}://{self.proxy['username']}:{self.proxy['password']}@{self.proxy['ip']}:{self.proxy['port']}",
               "https": f"{self.proxy['protocol']}s://{self.proxy['username']}:{self.proxy['password']}@{self.proxy['ip']}:{self.proxy['port']}",
               "no_proxy": "localhost,127.0.0.1"
               }
             }
        
        # Chrome
        self.service = Service(executable_path=self.DRIVER_PATH)
        self.options: webdriver.ChromeOptions = webdriver.ChromeOptions()
        
        prefs: dict[str] = {
               "profile.default_content_setting_values.notifications": 1,
          }
        self.options.add_experimental_option("prefs", prefs)
        self.options.add_argument("--headless")
        self.options.add_argument('--no-sandbox')
        self.options.add_argument("--disable-infobars")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-gpu")  
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument('--disable-sync')
        self.options.add_argument('--disable-translate')
        self.options.add_argument('--safebrowsing-disable-auto-update')
        self.options.add_argument("--disable-features=VizDisplayCompositor") 
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument(
             f"--window-size={random.randint(800, 1920)},{random.randint(600, 1080)}")
        
        self.driver = webdriver.Chrome(options=self.options, seleniumwire_options=self.proxy_options, service=self.service)

        # Random Headers & Random User-Agent
        self.random_headers: dict[str] = Headers(headers=True).generate()
        self.random_user_agents: str = self.random_headers['User-Agent']

        logger.success(
             f"""\nAll settings for {self.url}: 
             \nDelay on page - {self.DELAY_ON_PAGE}
             \nRandom page count - {self.RANDOM_PAGE_COUNTS}
             \nScroll delay min/max - {self.SCROLL_DELAY_MIN}/{self.SCROLL_DELAY_MAX}
             \nScroll step min/max - {self.SCROLL_STEP_MIN}/{self.SCROLL_STEP_MAX}
             \nProxy - {self.proxy['protocol']}://{self.proxy['ip']}
             \nHeaders - {self.random_headers}"""
        )
        logger.success('Initialize Class')
     
     @logger.catch
     def smooth_scroll(self) -> None:
          self.driver.implicitly_wait(random.randint(2, 6))
          page_height = self.driver.execute_script("return document.body.scrollHeight")
          window_height = self.driver.execute_script("return window.innerHeight")

          if page_height <= window_height:
               logger.info(f"No need to scroll. {self.driver.current_url}")
               return

          current_position = 0
          end_position = random.randint(150, 1500)
          scroll_step = random.randint(self.SCROLL_STEP_MIN, self.SCROLL_STEP_MAX)

          while current_position < end_position:
               logger.info(f'Position from/to ({self.driver.current_url}): {current_position} / {end_position}')
               current_position += scroll_step
               self.driver.execute_script(f"window.scrollTo(0, {current_position});")
               scroll_step = random.randint(self.SCROLL_STEP_MIN, self.SCROLL_STEP_MAX)
               time.sleep(random.uniform(self.SCROLL_DELAY_MIN, self.SCROLL_DELAY_MAX))
     
     @logger.catch
     def is_valid_link(self, links: str) -> bool:
          correct_links = []
          
          base_domain = urlparse(self.driver.current_url).netloc
          current_url = self.driver.current_url
          
          for l in links:
               link_url = l.get_attribute('href')
               link_domain = urlparse(link_url).netloc
                              
               if link_domain != base_domain or link_url.endswith('/#') or link_url == current_url or l is None:
                    continue
               else:
                    correct_links.append(l)
          return correct_links

     @logger.catch
     def random_link(self) -> str:
          links_from_page = self.driver.find_elements(By.TAG_NAME, 'a')
          logger.info(f'All links on page {len(links_from_page)}')
          
          links = []
          for l in links_from_page:
               if l.is_displayed() and l.is_enabled():
                    links.append(l)
          
          r_link: str = random.choice(self.is_valid_link(links))
          return r_link

     
     @logger.catch
     def click_to_link(self) -> None:
          WebDriverWait(self.driver, self.DELAY_ON_PAGE).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
          )
          
          random_link: str = self.random_link
          
          time.sleep(4)
          
          try:
               self.driver.execute_script('arguments[0].click();', random_link())
               asyncio.run(send_stat('links', self.driver.current_url))
               logger.success('Execute click!')
          except (selenium.common.exceptions.JavascriptException,
                  selenium.common.exceptions.ElementNotInteractableException, 
                  selenium.common.exceptions.ElementClickInterceptedException) as ex:
               logger.info('Execute get method!')
               logger.error(f'Error on click to random link ->  {ex}')
               self.driver.get(random_link().get_attribute('href'))
               asyncio.run(send_stat('links', self.driver.current_url))
               
               WebDriverWait(self.driver, self.DELAY_ON_PAGE).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
               )
               
          self.smooth_scroll()     
          time.sleep(self.DELAY_ON_PAGE)
          
          for _ in range(self.RANDOM_PAGE_COUNTS):
               WebDriverWait(self.driver, self.DELAY_ON_PAGE).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
               )
               logger.info(f"\nPage current count: {_} --- Counts: {self.RANDOM_PAGE_COUNTS} \n Page: {self.driver.current_url}")
               try:
                    self.driver.execute_script('arguments[0].click();', random_link())
               except selenium.common.exceptions.JavascriptException:
                    self.driver.back()
                    time.sleep(2)
                    self.driver.execute_script('arguments[0].click();', random_link())
          
               time.sleep(self.DELAY_ON_PAGE)
               self.smooth_scroll()
               asyncio.run(send_stat('links', self.driver.current_url))
          
          time.sleep(self.DELAY_ON_PAGE)
     
     def start_bot(self) -> None:
          logger.success(f'Starting Bot')
          self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
          self.driver.execute_script("""Object.defineProperty(navigator, 'userAgent', {get: () => arguments[0]})""", self.random_user_agents)
          self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": self.random_user_agents,"platform": "Windows"})
          self.driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {'headers': self.random_headers})

          try:
               logger.info(f'Request to the url: {self.url}')
               self.driver.get(self.url)

               WebDriverWait(self.driver, self.DELAY_ON_PAGE).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
               )

               logger.info('1. Smooth scrolling')

               self.smooth_scroll()
               

               logger.info(f'1. Going to the random pages {self.url}')
               self.click_to_link()
               logger.info(f"Cookies: {self.driver.get_cookies()}")

          except Exception as e:
               logger.error(f'Error on main function {e} {self.driver.current_url}')
          finally:
               try:
                    time.sleep(self.DELAY_ON_PAGE)
                    self.driver.delete_all_cookies()
                    logger.info('Deleting cookies')
                    asyncio.run(send_stat('interval'))
                    logger.success(f'Quiting the driver {self.driver.current_url}')
                    self.driver.close()
                    self.driver.quit()
               except Exception as e:
                    import sys
                    logger.error(f'Error while quiting the driver {e} {self.driver.current_url}')
                    sys.exit()
     

if __name__ == "__main__":
    from multiprocessing import Process
    logger.success(f'URLs: {AdBot.url_from_api}')
    
    def start(url):
         AdBot(url).start_bot()
    
    try:
        processes = []
        for url in AdBot.url_from_api:
            process = Process(target=start, args=(url,))
            processes.append(process)
            process.start()

        for process in processes:
            process.join()
            
    except KeyboardInterrupt as ex:
        pass