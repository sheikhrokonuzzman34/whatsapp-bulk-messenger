import logging
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Config
NEW_MSG_TIME = 20  # Time for a new message (in seconds)
SEND_MSG_TIME = 5  # Time for sending a message (in seconds)
COUNTRY_CODE = 880  # Set your country code
ACTION_TIME = 2  # Set time for button click action
IMAGE_PATH = None  # Path to image if you want to send
MESSAGE_FILE = 'message.txt'  # Path to message file
NUMBERS_FILE = 'numbers.txt'  # Path to numbers file

# Set the path to your Edge user data directory
# You need to replace this with the actual path on your system
USER_DATA_DIR = r"C:\Users\Universe soft care\AppData\Local\Microsoft\Edge\User Data"
PROFILE_DIR = "Default"  # or the name of the profile you want to use

def create_driver():
    options = webdriver.EdgeOptions()
    options.add_argument(f"user-data-dir={USER_DATA_DIR}")
    options.add_argument(f"profile-directory={PROFILE_DIR}")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.page_load_strategy = 'eager'

    # Use the default Edge installation
    service = EdgeService()
    driver = webdriver.Edge(service=service, options=options)
    return driver

def wait_for_element(driver, locator, timeout=20):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))

def send_message(driver, phone_number, message, image_path=None):
    try:
        # Construct and navigate to the WhatsApp chat URL
        chat_url = f'https://web.whatsapp.com/send/?phone={COUNTRY_CODE}{phone_number}'
        driver.get(chat_url)
        logging.info(f"Navigated to chat for {phone_number}")

        # Wait for the chat input box to load
        message_box = wait_for_element(driver, (By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
        logging.info(f"Chat input box found for {phone_number}")

        time.sleep(NEW_MSG_TIME)  # Give some time for the page to fully load

        # Attach image if provided
        if image_path:
            attach_button = wait_for_element(driver, (By.CSS_SELECTOR, 'span[data-icon="attach-menu-plus"]'))
            attach_button.click()
            time.sleep(ACTION_TIME)

            image_input = wait_for_element(driver, (By.CSS_SELECTOR, 'input[type="file"]'))
            image_input.send_keys(image_path)
            time.sleep(ACTION_TIME)

            # Wait for the image to upload
            wait_for_element(driver, (By.XPATH, '//div[@data-icon="send"]'))

        # Send the message
        actions = ActionChains(driver)
        for line in message.split('\n'):
            actions.send_keys(line)
            actions.key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT)
        actions.send_keys(Keys.ENTER)
        actions.perform()

        logging.info(f"Message sent to {phone_number}")
        time.sleep(SEND_MSG_TIME)

    except TimeoutException:
        logging.error(f"Timeout occurred while sending message to {phone_number}")
    except NoSuchElementException as e:
        logging.error(f"Element not found: {e}")
    except Exception as e:
        logging.error(f"An error occurred while sending message to {phone_number}: {e}")


    
    
def main():
    driver = create_driver()
    logging.info("WebDriver created")

    try:
        # Open WhatsApp Web
        driver.get('https://web.whatsapp.com')
        logging.info("WhatsApp Web opened")

        # Check if logged in by continuously checking for the chat box
        while True:
            try:
                # If this element is found, it means the user is logged in
                wait_for_element(driver, (By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'), timeout=10)
                logging.info("Successfully logged in to WhatsApp Web")
                break  # Exit the loop as login is successful
            except TimeoutException:
                logging.info("Waiting for QR code scan. Please scan the QR code...")
                time.sleep(5)  # Retry every 5 seconds

        # Read message
        with open(MESSAGE_FILE, 'r', encoding='utf-8') as file:
            message = file.read()

        # Read and process phone numbers
        with open(NUMBERS_FILE, 'r') as file:
            phone_numbers = [line.strip() for line in file if line.strip()]

        for phone_number in phone_numbers:
            send_message(driver, phone_number, message, IMAGE_PATH)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        driver.quit()
        logging.info("WebDriver closed")

if __name__ == "__main__":
    main()    
    
    
    
    
    
