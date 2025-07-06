from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def get_wallet_balance(wallet_address):
    # Setup Chrome WebDriver using Selenium
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # Construct the URL using the wallet address
    url = f'https://sei.blockscout.com/address/{wallet_address}'

    # Open the page in the browser
    driver.get(url)

    # Wait for the balance element to load dynamically
    try:
        # Wait until the element containing balance is present
        balance_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[@class='css-1baulvz']"))
        )

        # Extract and print the balance
        balance = balance_element.text
        print(f"Wallet Balance: {balance}")

        # Optionally, extract the USD value if available
        usd_value_element = driver.find_element(By.XPATH, "//span[@class='css-1st9hq1']")
        usd_value = usd_value_element.text if usd_value_element else "USD Value not available"
        print(f"USD Value: {usd_value}")
    
    except Exception as e:
        print(f"Error finding balance: {e}")
    finally:
        # Close the browser
        driver.quit()

# User input for wallet address
wallet_address = "0x6Ae3539c7BB31AbCaCc2403e7F6091BC43D825FF"

# Call the function to get the wallet balance
get_wallet_balance(wallet_address)
