from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

TIMEOUT_DURATION = 300


class children_changed(object):
    """An expectation to check if the children of the provided element have changed."""

    def __init__(self, element, initial_state):
        self.element = element
        self.initial_state = initial_state

    def __call__(self, driver):
        current_state = [
            child.text for child in self.element.find_elements(By.XPATH, "./*")
        ]
        return current_state != self.initial_state


def download_fba_inv(seller_central, REPORT_FBA_INV):
    seller_central.driver_actions.get(REPORT_FBA_INV)
    seller_central.driver_actions.click_element(
        By.XPATH, '//*[@id="report-page-kat-box"]/kat-button[1]'
    )

    progress_element_parent = seller_central.driver_actions.get_element(
        By.XPATH, "//*[text()='In Progress']/.."
    )

    descendant_elements = progress_element_parent.find_elements(By.XPATH, ".//*")

    initial_state = [
        child.text for child in progress_element_parent.find_elements(By.XPATH, "./*")
    ]

    # Wait for the child elements to change
    WebDriverWait(seller_central.driver_actions.driver, TIMEOUT_DURATION).until(
        children_changed(progress_element_parent, initial_state)
    )
    descendant_elements = progress_element_parent.find_elements(By.XPATH, ".//*")
    # Once the change is detected, click on the desired descendant
    descendant_elements[0].click()
