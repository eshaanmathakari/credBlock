import datetime
import random
import json
import os
import web3
from web3 import Web3
from dotenv import load_dotenv
import time

load_dotenv()

# File to store the last processed block number in the current working directory
LAST_PROCESSED_BLOCK_FILE = os.path.join(os.getcwd(), "last_processed_block.txt")

# --- Helper functions for managing last processed block ---
def save_last_processed_block(block_number):
    try:
        with open(LAST_PROCESSED_BLOCK_FILE, "w") as f:
            f.write(str(block_number))
        print(f"Saved last processed block: {block_number}")
    except IOError as e:
        print(f"Error saving last processed block: {e}")

def load_last_processed_block():
    if os.path.exists(LAST_PROCESSED_BLOCK_FILE):
        try:
            with open(LAST_PROCESSED_BLOCK_FILE, "r") as f:
                block_number = int(f.read().strip())
            print(f"Loaded last processed block: {block_number}")
            return block_number
        except (IOError, ValueError) as e:
            print(f"Error loading last processed block: {e}. Starting from 0.")
            return 0
    return 0 # Start from block 0 if file doesn't exist

# --- Placeholder Data Simulation (Replace with actual Sei Network API calls) ---

def simulate_get_wallet_creation_date(wallet_address):
    """
    Simulates fetching the wallet creation date.
    In a real scenario, this would involve querying the blockchain for the
    first transaction of the wallet address.
    """
    if wallet_address.startswith("0x1"):  # Older wallet
        return datetime.datetime.now() - datetime.timedelta(days=random.randint(365 * 2, 365 * 5))
    elif wallet_address.startswith("0x2"):  # Medium age wallet
        return datetime.datetime.now() - datetime.timedelta(days=random.randint(180, 365 * 1))
    elif wallet_address.startswith("0x3"):  # Newer wallet, potentially risky
        return datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 179))
    else:  # Default for other random addresses
        return datetime.datetime.now() - datetime.timedelta(days=random.randint(30, 730))

def simulate_get_transaction_history(wallet_address, lookback_days=365):
    """
    Simulates fetching transaction history for a given wallet address.
    """
    num_txns = 0
    total_volume_usd = 0.0
    unique_contracts = set()
    suspicious_interaction = False

    if wallet_address.startswith("0x1"):  # High activity, good
        num_txns = random.randint(500, 2000)
        total_volume_usd = random.uniform(10000, 100000)
        unique_contracts = set(f"0xContract{i}" for i in range(random.randint(10, 30)))
    elif wallet_address.startswith("0x2"):  # Medium activity
        num_txns = random.randint(100, 500)
        total_volume_usd = random.uniform(1000, 10000)
        unique_contracts = set(f"0xContract{i}" for i in range(random.randint(3, 9)))
    elif wallet_address.startswith("0x3"):  # Low activity, potentially suspicious
        num_txns = random.randint(5, 50)
        total_volume_usd = random.uniform(10, 500)
        unique_contracts = set(f"0xContract{i}" for i in range(random.randint(1, 2)))
        if random.random() < 0.7:
            suspicious_interaction = True
    else:  # Default for other random addresses
        num_txns = random.randint(20, 300)
        total_volume_usd = random.uniform(100, 5000)
        unique_contracts = set(f"0xContract{i}" for i in range(random.randint(2, 15)))
        if random.random() < 0.1:
            suspicious_interaction = True

    return {
        "num_transactions": num_txns,
        "total_volume_usd": total_volume_usd,
        "unique_contracts_interacted_with": list(unique_contracts),
        "suspicious_interaction": suspicious_interaction
    }

def simulate_get_wallet_balances(wallet_address):
    """
    Simulates fetching current wallet balances.
    """
    balances = {}
    if wallet_address.startswith("0x1"):  # High value, good stablecoin ratio
        balances["SEI"] = random.uniform(1000, 5000)
        balances["USDC"] = random.uniform(5000, 20000)
        balances["ETH"] = random.uniform(1, 5)
    elif wallet_address.startswith("0x2"):  # Medium value
        balances["SEI"] = random.uniform(100, 1000)
        balances["USDC"] = random.uniform(500, 5000)
    elif wallet_address.startswith("0x3"):  # Low value, mostly volatile
        balances["SEI"] = random.uniform(10, 100)
        balances["USDT"] = random.uniform(0, 50)
    else:  # Default for other random addresses
        balances["SEI"] = random.uniform(50, 500)
        balances["USDC"] = random.uniform(100, 1000)
        if random.random() < 0.2:
            balances["SOME_ALT_COIN"] = random.uniform(10, 200)

    return balances

def get_batched_logs(event, from_block, to_block, batch_size=1000, **kwargs):
    """
    Fetches event logs in batches to avoid 'block range too large' errors.
    """
    all_logs = []
    current = from_block
    
    while current <= to_block:
        batch_end = min(current + batch_size - 1, to_block)
        try:
            logs = event.get_logs(from_block=current, to_block=batch_end, **kwargs)
            all_logs.extend(logs)
            print(f"   Fetched {len(logs)} events from blocks {current} to {batch_end}")
        except Exception as e:
            print(f"   Error fetching logs from blocks {current} to {batch_end}: {e}")
        
        current = batch_end + 1
        # Small delay to avoid rate limiting
        time.sleep(0.1)
    
    return all_logs

def get_loan_repayment_history(wallet_address, contract, w3, start_block=0):
    """
    Fetches and combines borrow, repay, and liquidation events for a given wallet
    from the Aave V3-style lending pool using batched queries.
    """
    history = []
    
    print(f"🔍 Fetching transaction history for {wallet_address} from block {start_block}...")
    
    try:
        # Get the latest block number
        latest_block = w3.eth.block_number
        print(f"   Latest block: {latest_block}")
        
        # 1. Fetch Borrow events in batches
        print("   Fetching Borrow events...")
        borrow_events = get_batched_logs(
            contract.events.Borrow(),
            from_block=start_block,
            to_block=latest_block,
            argument_filters={'user': wallet_address}
        )
        
        for event in borrow_events:
            history.append({
                'type': 'Borrow',
                'user': event['args']['onBehalfOf'],
                'reserve': event['args']['reserve'],
                'amount': event['args']['amount'],
                'blockNumber': event['blockNumber'],
                'transactionHash': event['transactionHash'].hex()
            })
        print(f"   Found {len(borrow_events)} Borrow event(s).")

        # 2. Fetch Repay events in batches
        print("   Fetching Repay events...")
        repay_events = get_batched_logs(
            contract.events.Repay(),
            from_block=start_block,
            to_block=latest_block,
            argument_filters={'user': wallet_address}
        )
        
        for event in repay_events:
            history.append({
                'type': 'Repay',
                'user': event['args']['user'],
                'repayer': event['args']['repayer'],
                'reserve': event['args']['reserve'],
                'amount': event['args']['amount'],
                'blockNumber': event['blockNumber'],
                'transactionHash': event['transactionHash'].hex()
            })
        print(f"   Found {len(repay_events)} Repay event(s).")

        # 3. Fetch LiquidationCall events in batches
        print("   Fetching LiquidationCall events...")
        liquidation_events = get_batched_logs(
            contract.events.LiquidationCall(),
            from_block=start_block,
            to_block=latest_block,
            argument_filters={'user': wallet_address}
        )
        
        for event in liquidation_events:
            history.append({
                'type': 'Liquidation',
                'user': event['args']['user'],
                'collateralAsset': event['args']['collateralAsset'],
                'debtAsset': event['args']['debtAsset'],
                'debtToCover': event['args']['debtToCover'],
                'liquidatedCollateralAmount': event['args']['liquidatedCollateralAmount'],
                'liquidator': event['args']['liquidator'],
                'blockNumber': event['blockNumber'],
                'transactionHash': event['transactionHash'].hex()
            })
        print(f"   Found {len(liquidation_events)} LiquidationCall event(s).")

        # Sort the combined history by block number to ensure chronological order
        history.sort(key=lambda x: x['blockNumber'])
        
        # Save the latest block processed for the next run
        save_last_processed_block(latest_block)

        return history

    except Exception as e:
        print(f"An error occurred while fetching event logs: {e}")
        # Return empty history instead of raising to allow the script to continue
        return []

def get_protocol_interactions(wallet_address):
    """Retrieve staking, LP and governance participation information for an address."""
    # For simulation purposes, return mock data
    # In a real implementation, this would query actual contracts
    return {
        "is_staker": random.choice([True, False]),
        "is_lp_provider": random.choice([True, False]),
        "num_governance_votes": random.randint(0, 10),
        "total_staked_sei": random.uniform(0, 1000),
        "total_lp_value_usd": random.uniform(0, 5000),
    }

class DeFiCreditScorer:
    BASE_SCORE = 500  # Starting score

    def __init__(self,lending_pool_addr: str, abi_path: str = "C:/Users/DEVANKSH/defi-credit-tracker/backend/abis/yei-pool.json"):
        """
        Constructor for the DeFiCreditScorer.
        This now includes the setup for Web3 connection and contract initialization.
        """
        # --- 1. SET UP CONNECTION TO THE BLOCKCHAIN ---
        self.rpc_url = "https://evm-rpc.sei-apis.com/"
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        if not self.w3.isConnected():
            raise ConnectionError("Failed to connect to the Sei EVM RPC.")

        # --- 2. DEFINE CONTRACT ADDRESS AND ABI ---
        # Replace with your actual deployed lending pool contract address
        self.contract_address = "0xA1b2C3d4E5f678901234567890abcdef12345678"
        
        # Load the contract's ABI from the JSON file
        with open('C:/Users/DEVANKSH/defi-credit-tracker/backend/abis/yei-pool.json', 'r') as f:
            contract_abi = json.load(f)

        # --- 3. CREATE AND STORE THE CONTRACT OBJECT ---
        self.contract = self.w3.eth.contract(
            address=self.w3.toChecksumAddress(self.contract_address),
            abi=contract_abi
        )
        
        print("DeFiCreditScorer initialized and connected to the contract.")

    def _calculate_account_age_score(self, wallet_creation_date):
        """Calculates score based on account age."""
        age_days = (datetime.datetime.now() - wallet_creation_date).days
        score_contribution = 0
        
        if age_days < 90:
            score_contribution = -50
        elif 90 <= age_days < 180:
            score_contribution = -20
        elif 180 <= age_days < 365:
            score_contribution = 10
        elif 365 <= age_days < 730:
            score_contribution = 25
        else:
            score_contribution = 40
            
        return score_contribution, f"Account Age ({age_days} days)"

    def _calculate_repayment_behavior_score(self, loan_history):
        """Calculates score based on historical loan repayment behavior."""
        if not loan_history:
            return 0, "Repayment Behavior (No prior loans)"
        
        # For simulation, we'll create mock repayment data based on the events
        # In a real implementation, you'd analyze the actual loan lifecycle
        total_loans = len([event for event in loan_history if event['type'] == 'Borrow'])
        liquidations = len([event for event in loan_history if event['type'] == 'Liquidation'])
        
        if total_loans == 0:
            return 0, "Repayment Behavior (No loans found)"
        
        score_contribution = 0
        if liquidations > 0:
            score_contribution -= (liquidations * 150)
            return score_contribution, f"Repayment Behavior ({liquidations} liquidations)"
        else:
            score_contribution += 50  # Bonus for no liquidations
            return score_contribution, f"Repayment Behavior (No liquidations, {total_loans} loans)"

    def _calculate_transaction_history_score(self, txn_history):
        """Calculates score based on transaction frequency, volume, and patterns."""
        score_contribution = 0
        num_txns = txn_history["num_transactions"]
        total_volume_usd = txn_history["total_volume_usd"]
        num_unique_contracts = len(txn_history["unique_contracts_interacted_with"])
        suspicious_interaction = txn_history["suspicious_interaction"]

        # Transaction Frequency
        if num_txns > 500:
            score_contribution += 40
        elif num_txns > 100:
            score_contribution += 20
        elif num_txns > 20:
            score_contribution += 5
        else:
            score_contribution -= 10

        # Total Volume
        if total_volume_usd > 10000:
            score_contribution += 30
        elif total_volume_usd > 1000:
            score_contribution += 15
        else:
            score_contribution -= 5

        # Diversity of Interactions
        if num_unique_contracts > 10:
            score_contribution += 20
        elif num_unique_contracts > 3:
            score_contribution += 10
        else:
            score_contribution -= 5

        # Suspicious Interaction Flag
        if suspicious_interaction:
            score_contribution -= 300

        return score_contribution, f"Transaction History (Txns: {num_txns}, Volume: ${total_volume_usd:,.0f}, Contracts: {num_unique_contracts})"

    def _calculate_wallet_balance_score(self, balances):
        """Calculates score based on wallet balances, liquidity, and diversity."""
        total_value_usd = 0
        stablecoin_value_usd = 0
        num_unique_tokens = 0

        for token, amount in balances.items():
            if token == "SEI":
                total_value_usd += amount * 0.5
            elif token == "ETH":
                total_value_usd += amount * 3000
            elif token in ["USDC", "USDT"]:
                total_value_usd += amount
                stablecoin_value_usd += amount
            num_unique_tokens += 1

        score_contribution = 0
        stablecoin_ratio = (stablecoin_value_usd / total_value_usd) * 100 if total_value_usd > 0 else 0

        # Total Value
        if total_value_usd > 10000:
            score_contribution += 60
        elif total_value_usd > 1000:
            score_contribution += 30
        else:
            score_contribution -= 20

        # Stablecoin Ratio
        if stablecoin_ratio > 50:
            score_contribution += 25
        elif stablecoin_ratio > 20:
            score_contribution += 10
        else:
            score_contribution -= 10

        # Diversity of Holdings
        if num_unique_tokens > 5:
            score_contribution += 15
        elif num_unique_tokens > 2:
            score_contribution += 5

        return score_contribution, f"Wallet Balances (Total: ${total_value_usd:,.0f}, Stablecoin Ratio: {stablecoin_ratio:.0f}%)"

    def _calculate_protocol_interaction_score(self, protocol_interactions):
        """Calculates score based on engagement with other DeFi protocols."""
        score_contribution = 0
        is_staker = protocol_interactions["is_staker"]
        is_lp_provider = protocol_interactions["is_lp_provider"]
        num_governance_votes = protocol_interactions["num_governance_votes"]
        total_staked_sei = protocol_interactions["total_staked_sei"]
        total_lp_value_usd = protocol_interactions["total_lp_value_usd"]

        if is_staker and total_staked_sei > 1000:
            score_contribution += 20
        elif is_staker:
            score_contribution += 5

        if is_lp_provider and total_lp_value_usd > 1000:
            score_contribution += 20
        elif is_lp_provider:
            score_contribution += 5

        if num_governance_votes > 5:
            score_contribution += 15
        elif num_governance_votes > 0:
            score_contribution += 5

        return score_contribution, f"Protocol Interactions (Staker: {is_staker}, LP: {is_lp_provider}, Votes: {num_governance_votes})"

    def calculate_credit_score(self, wallet_address):
        """
        Calculates the overall credit score for a given wallet address
        by aggregating scores from various factors.
        """
        detailed_scores = []
        current_score = self.BASE_SCORE

        # Load the last processed block number
        start_block_for_events = load_last_processed_block()

        # 1. Fetch data from the Sei network
        wallet_creation_date = simulate_get_wallet_creation_date(wallet_address)
        txn_history = simulate_get_transaction_history(wallet_address)
        wallet_balances = simulate_get_wallet_balances(wallet_address)
        loan_history = get_loan_repayment_history(wallet_address, self.contract, self.w3, start_block=start_block_for_events)
        protocol_interactions = get_protocol_interactions(wallet_address)

        # 2. Calculate scores for each factor
        score, description = self._calculate_account_age_score(wallet_creation_date)
        current_score += score
        detailed_scores.append({"factor": "Account Age", "contribution": score, "description": description})

        score, description = self._calculate_repayment_behavior_score(loan_history)
        current_score += score
        detailed_scores.append({"factor": "Repayment Behavior", "contribution": score, "description": description})

        score, description = self._calculate_transaction_history_score(txn_history)
        current_score += score
        detailed_scores.append({"factor": "Transaction History", "contribution": score, "description": description})

        score, description = self._calculate_wallet_balance_score(wallet_balances)
        current_score += score
        detailed_scores.append({"factor": "Wallet Balances", "contribution": score, "description": description})

        score, description = self._calculate_protocol_interaction_score(protocol_interactions)
        current_score += score
        detailed_scores.append({"factor": "Protocol Interactions", "contribution": score, "description": description})

        # Ensure score doesn't go below 0 or above 1000
        final_score = max(0, min(1000, current_score))

        # Determine risk category
        risk_category = "Unknown"
        if final_score < 300:
            risk_category = "Very High Risk"
        elif 300 <= final_score < 500:
            risk_category = "High Risk"
        elif 500 <= final_score < 700:
            risk_category = "Medium Risk"
        elif 700 <= final_score < 850:
            risk_category = "Low Risk"
        else:
            risk_category = "Very Low Risk"

        return {
            "wallet_address": wallet_address,
            "credit_score": final_score,
            "risk_category": risk_category,
            "detailed_scores": detailed_scores,
            "raw_data_simulated": {
                "wallet_creation_date": wallet_creation_date.isoformat(),
                "transaction_history": txn_history,
                "wallet_balances": wallet_balances,
                "loan_repayment_history": loan_history,
                "protocol_interactions": protocol_interactions
            }
        }

# --- Dynamic Example Usage ---
if __name__ == "__main__":
    scorer = DeFiCreditScorer()
    
    print("\n--- AI-Powered DeFi Risk Assessment Tool (Simulated) ---")
    print("Enter a Sei wallet address to get its simulated credit score.")
    print("Note: This uses simulated data. For real data, you need to integrate with Sei Network's RPC.")
    print("Try addresses starting with '0x1' for good scores, '0x2' for medium, '0x3' for potentially risky.")
    print("You can also enter any other valid-looking hex address for a mixed simulated result.")
    
    while True:
        wallet_input = input("\nEnter Sei Wallet Address (or 'quit' to exit): ").strip()
        
        if wallet_input.lower() == 'quit':
            break
        
        # Basic validation for a hex address
        if not (wallet_input.startswith("0x") and len(wallet_input) >= 42):
            print("Invalid wallet address format. Please enter a valid hex address (e.g., 0x...). ")
            continue
        
        print(f"\n--- Assessing Wallet: {wallet_input} ---")
        score_result = scorer.calculate_credit_score(wallet_input)
        
        print(f"\nSummary for {wallet_input}:")
        print(f" Credit Score: {score_result['credit_score']}")
        print(f" Risk Category: {score_result['risk_category']}")
        print("\n Detailed Contributions:")
        for detail in score_result['detailed_scores']:
            print(f" - {detail['factor']}: {detail['contribution']} points ({detail['description']})")


