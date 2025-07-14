import requests

def get_wallet_info(wallet_address):
    # API URL for fetching wallet info
    url = f'https://sei.blockscout.com/api/v2/addresses/{wallet_address}'
    
    # Set the header
    headers = {'accept': 'application/json'}

    try:
        # Make the GET request to the API
        response = requests.get(url, headers=headers)

        # Print the response status to debug
        print(f"Response Status Code: {response.status_code}")

        # Check if the response was successful
        if response.status_code == 200:
            # Parse the response JSON
            data = response.json()

            # Check if the data exists and contains relevant information
            if data:
                return data
            else:
                print("No data available for this address.")
                return None
        else:
            print(f"Error: Unable to fetch data. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        # Handle network or other request exceptions
        print(f"Error: {e}")
        return None

# Example usage with a specific wallet address
wallet_address = "0x6Ae3539c7BB31AbCaCc2403e7F6091BC43D825FF"
wallet_info = get_wallet_info(wallet_address)

# Print the wallet info if available
if wallet_info:
    print("Wallet Info:", wallet_info)
else:
    print("No wallet information returned.")
