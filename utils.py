from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def search_element_by_locator_strategy(browser, locator_strategy, element_xpath):
    i = 0
    while i < 4:
        try:
            element = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((locator_strategy, element_xpath))
            )
            if element:
                return element
        except TimeoutException as timeout:
            i += 1


def perform_click_on_element(browser, on_element):
    action = ActionChains(browser.driver)
    action.move_to_element(on_element)
    action.click(on_element)
    action.perform()
