import requests
from bs4 import BeautifulSoup
import warnings

# Suppress SSL warning
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Replace with the URL you want to fetch
url = 'https://testnet.sei.explorers.guru/'

# Send a GET request to the URL
response = requests.get(url, verify=False)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the page content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Example: Find all the <h1> headers
    headers = soup.find_all('h1')
    for header in headers:
        print(header.text)
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
