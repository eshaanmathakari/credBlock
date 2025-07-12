import requests
import pandas as pd
from datetime import datetime

# API endpoint and headers
url = "https://sei.blockscout.com/api/v2/addresses/0x2a45907f94df93388801AE72fE810eac75926a1d/transactions"
headers = {'accept': 'application/json'}

# Send GET request
response = requests.get(url, headers=headers)

# Check if the response is successful
if response.status_code == 200:
    data = response.json()
    
    # Extract transaction items
    transactions = data.get('items', [])
    
    # Convert transaction timestamps to pandas dataframe
    df = pd.DataFrame(transactions)
    
    # Ensure the timestamp column is in datetime format
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Group by week and count transactions
    df['week'] = df['timestamp'].dt.to_period('W')
    transaction_counts = df.groupby('week').size().reset_index(name='transaction_count')
    
    # Display weekly transaction counts
    print(transaction_counts)
else:
    print(f"Error fetching data: {response.status_code}")
