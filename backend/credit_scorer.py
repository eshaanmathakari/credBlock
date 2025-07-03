import datetime
import random
import json

# --- Placeholder Data Simulation (Replace with actual Sei Network API calls) ---
# In a real application, these functions would interact with Sei's EVM RPC
# (e.g., using web3.py or ethers.js equivalents in Python) to fetch on-chain data.
# You would need to connect to an RPC endpoint like 'https://evm-rpc.sei-apis.com'.

def simulate_get_wallet_creation_date(wallet_address):
    """
    Simulates fetching the wallet creation date.
    In a real scenario, this would involve querying the blockchain for the
    first transaction of the wallet address.
    """
    # For demonstration, we'll make the age somewhat dependent on the first character
    # to show different scores for different "types" of addresses.
    # In a real scenario, this would be based on actual on-chain data.
    if wallet_address.startswith("0x1"): # Older wallet
        return datetime.datetime.now() - datetime.timedelta(days=random.randint(365 * 2, 365 * 5))
    elif wallet_address.startswith("0x2"): # Medium age wallet
        return datetime.datetime.now() - datetime.timedelta(days=random.randint(180, 365 * 1))
    elif wallet_address.startswith("0x3"): # Newer wallet, potentially risky
        return datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 179))
    else: # Default for other random addresses
        return datetime.datetime.now() - datetime.timedelta(days=random.randint(30, 730)) # Mix of ages


def simulate_get_transaction_history(wallet_address, lookback_days=365):
    """
    Simulates fetching transaction history for a given wallet address.
    In a real scenario, this would query Sei's RPC for transactions
    associated with the address within the specified lookback period.
    Returns a list of dictionaries, each representing a transaction.
    """
    num_txns = 0
    total_volume_usd = 0.0
    unique_contracts = set()
    suspicious_interaction = False

    if wallet_address.startswith("0x1"): # High activity, good
        num_txns = random.randint(500, 2000)
        total_volume_usd = random.uniform(10000, 100000)
        unique_contracts = set(f"0xContract{i}" for i in range(random.randint(10, 30)))
    elif wallet_address.startswith("0x2"): # Medium activity
        num_txns = random.randint(100, 500)
        total_volume_usd = random.uniform(1000, 10000)
        unique_contracts = set(f"0xContract{i}" for i in range(random.randint(3, 9)))
    elif wallet_address.startswith("0x3"): # Low activity, potentially suspicious
        num_txns = random.randint(5, 50)
        total_volume_usd = random.uniform(10, 500)
        unique_contracts = set(f"0xContract{i}" for i in range(random.randint(1, 2)))
        if random.random() < 0.7: # Higher chance of suspicious interaction for "risky" addresses
            suspicious_interaction = True
    else: # Default for other random addresses
        num_txns = random.randint(20, 300)
        total_volume_usd = random.uniform(100, 5000)
        unique_contracts = set(f"0xContract{i}" for i in range(random.randint(2, 15)))
        if random.random() < 0.1: # Small chance of suspicious interaction
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
    In a real scenario, this would query Sei's RPC for token balances
    (e.g., SEI, stablecoins, other ERC-20 tokens).
    Returns a dictionary of token balances.
    """
    balances = {}
    if wallet_address.startswith("0x1"): # High value, good stablecoin ratio
        balances["SEI"] = random.uniform(1000, 5000)
        balances["USDC"] = random.uniform(5000, 20000)
        balances["ETH"] = random.uniform(1, 5)
    elif wallet_address.startswith("0x2"): # Medium value
        balances["SEI"] = random.uniform(100, 1000)
        balances["USDC"] = random.uniform(500, 5000)
    elif wallet_address.startswith("0x3"): # Low value, mostly volatile
        balances["SEI"] = random.uniform(10, 100)
        balances["USDT"] = random.uniform(0, 50) # Can be very low
    else: # Default for other random addresses
        balances["SEI"] = random.uniform(50, 500)
        balances["USDC"] = random.uniform(100, 1000)
        if random.random() < 0.2:
            balances["SOME_ALT_COIN"] = random.uniform(10, 200)
    return balances

def simulate_get_loan_repayment_history(wallet_address):
    """
    Simulates fetching historical loan repayment data on Sei-native protocols.
    This is the most challenging part to simulate accurately without a real Sei
    lending protocol's historical data.
    Returns a list of loan records, each with 'status' ('repaid', 'defaulted', 'late')
    and 'repayment_delay_days'.
    """
    if wallet_address.startswith("0x1"): # Excellent repayment history
        return [
            {"status": "repaid", "repayment_delay_days": 0},
            {"status": "repaid", "repayment_delay_days": 0},
            {"status": "repaid", "repayment_delay_days": 0},
            {"status": "repaid", "repayment_delay_days": 0},
            {"status": "repaid", "repayment_delay_days": 0}
        ]
    elif wallet_address.startswith("0x2"): # Mixed repayment history
        return [
            {"status": "repaid", "repayment_delay_days": 0},
            {"status": "repaid", "repayment_delay_days": 5},
            {"status": "repaid", "repayment_delay_days": 0},
            {"status": "defaulted", "repayment_delay_days": None}
        ]
    elif wallet_address.startswith("0x3"): # Poor or no repayment history
        return [
            {"status": "defaulted", "repayment_delay_days": None},
            {"status": "late", "repayment_delay_days": 10}
        ] if random.random() < 0.7 else [] # 70% chance of some bad history for "risky" wallets
    else: # Default for other random addresses
        if random.random() < 0.6: # 60% chance of having some history
            history = []
            num_loans = random.randint(1, 5)
            for _ in range(num_loans):
                status_choice = random.choices(["repaid", "late", "defaulted"], weights=[0.7, 0.2, 0.1], k=1)[0]
                if status_choice == "repaid":
                    history.append({"status": "repaid", "repayment_delay_days": 0})
                elif status_choice == "late":
                    history.append({"status": "late", "repayment_delay_days": random.randint(1, 15)})
                else:
                    history.append({"status": "defaulted", "repayment_delay_days": None})
            return history
        else:
            return []


def simulate_get_protocol_interactions(wallet_address):
    """
    Simulates fetching data on other protocol interactions (staking, LP, governance).
    """
    is_staker = False
    is_lp_provider = False
    num_governance_votes = 0
    total_staked_sei = 0.0
    total_lp_value_usd = 0.0

    if wallet_address.startswith("0x1"):
        is_staker = True
        is_lp_provider = True
        num_governance_votes = random.randint(5, 20)
        total_staked_sei = random.uniform(1000, 10000)
        total_lp_value_usd = random.uniform(5000, 50000)
    elif wallet_address.startswith("0x2"):
        is_staker = True
        num_governance_votes = random.randint(1, 5)
        total_staked_sei = random.uniform(100, 1000)
    else: # Default for other random addresses
        if random.random() < 0.4: is_staker = True
        if random.random() < 0.2: is_lp_provider = True
        num_governance_votes = random.randint(0, 3)
        total_staked_sei = random.uniform(0, 500)
        total_lp_value_usd = random.uniform(0, 2000)

    return {
        "is_staker": is_staker,
        "is_lp_provider": is_lp_provider,
        "num_governance_votes": num_governance_votes,
        "total_staked_sei": total_staked_sei,
        "total_lp_value_usd": total_lp_value_usd
    }

# --- DeFiCreditScorer Class ---

class DeFiCreditScorer:
    BASE_SCORE = 500  # Starting score

    def __init__(self):
        """
        Initializes the credit scorer.
        In a real application, you might initialize a connection to the Sei RPC here.
        """
        print("DeFiCreditScorer initialized. Remember to replace simulation functions with real Sei API calls!")

    def _calculate_account_age_score(self, wallet_creation_date):
        """
        Calculates score based on account age.
        """
        age_days = (datetime.datetime.now() - wallet_creation_date).days
        score_contribution = 0
        if age_days < 90:  # Less than 3 months
            score_contribution = -50
        elif 90 <= age_days < 180: # 3-6 months
            score_contribution = -20
        elif 180 <= age_days < 365: # 6-12 months
            score_contribution = 10
        elif 365 <= age_days < 730: # 1-2 years
            score_contribution = 25
        else: # 2+ years
            score_contribution = 40
        return score_contribution, f"Account Age ({age_days} days)"

    def _calculate_repayment_behavior_score(self, loan_history):
        """
        Calculates score based on historical loan repayment behavior.
        """
        if not loan_history:
            return 0, "Repayment Behavior (No prior loans)"

        total_loans = len(loan_history)
        successful_repayments = sum(1 for loan in loan_history if loan["status"] == "repaid")
        defaults = sum(1 for loan in loan_history if loan["status"] == "defaulted")
        late_repayments = sum(1 for loan in loan_history if loan["status"] == "late")
        total_delay_days = sum(loan["repayment_delay_days"] for loan in loan_history if loan["status"] == "late" and loan["repayment_delay_days"] is not None)

        score_contribution = 0
        repayment_rate = (successful_repayments / total_loans) * 100 if total_loans > 0 else 0

        if defaults > 0:
            score_contribution -= (defaults * 150) # Significant penalty per default
            return score_contribution, f"Repayment Behavior ({defaults} defaults)"

        if repayment_rate == 100:
            score_contribution += 100
        elif repayment_rate >= 90:
            score_contribution += 70
        elif repayment_rate >= 70:
            score_contribution += 30
        elif repayment_rate >= 50:
            score_contribution -= 20
        else:
            score_contribution -= 50

        if late_repayments > 0:
            avg_delay = total_delay_days / late_repayments
            if avg_delay > 7:
                score_contribution -= 20
            elif avg_delay > 3:
                score_contribution -= 5
        
        return score_contribution, f"Repayment Behavior ({repayment_rate:.0f}% success, {late_repayments} late)"

    def _calculate_transaction_history_score(self, txn_history):
        """
        Calculates score based on transaction frequency, volume, and patterns.
        """
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
            score_contribution -= 300 # Severe penalty

        return score_contribution, f"Transaction History (Txns: {num_txns}, Volume: ${total_volume_usd:,.0f}, Contracts: {num_unique_contracts})"

    def _calculate_wallet_balance_score(self, balances):
        """
        Calculates score based on wallet balances, liquidity, and diversity.
        """
        total_value_usd = 0
        stablecoin_value_usd = 0
        num_unique_tokens = 0

        # Assuming USDC/USDT are stablecoins for this simulation
        for token, amount in balances.items():
            # In a real scenario, you'd fetch real-time prices for each token
            # For simulation, we'll assume SEI/ETH have some value, stablecoins are 1 USD
            if token == "SEI":
                total_value_usd += amount * 0.5 # Example SEI price
            elif token == "ETH":
                total_value_usd += amount * 3000 # Example ETH price
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
        """
        Calculates score based on engagement with other DeFi protocols.
        """
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

        # 1. Fetch data (using simulation functions for now)
        wallet_creation_date = simulate_get_wallet_creation_date(wallet_address)
        txn_history = simulate_get_transaction_history(wallet_address)
        wallet_balances = simulate_get_wallet_balances(wallet_address)
        loan_history = simulate_get_loan_repayment_history(wallet_address)
        protocol_interactions = simulate_get_protocol_interactions(wallet_address)

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

        # Ensure score doesn't go below 0 or above 1000 (or your desired max)
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
            "raw_data_simulated": { # For debugging/transparency, showing what was simulated
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

        # Basic validation for a hex address (starts with 0x and is long enough)
        if not (wallet_input.startswith("0x") and len(wallet_input) >= 42): # Typical EVM address length
            print("Invalid wallet address format. Please enter a valid hex address (e.g., 0x...).")
            continue

        print(f"\n--- Assessing Wallet: {wallet_input} ---")
        score_result = scorer.calculate_credit_score(wallet_input)
        
        print(f"\nSummary for {wallet_input}:")
        print(f"  Credit Score: {score_result['credit_score']}")
        print(f"  Risk Category: {score_result['risk_category']}")
        print("\n  Detailed Contributions:")
        for detail in score_result['detailed_scores']:
            print(f"    - {detail['factor']}: {detail['contribution']} points ({detail['description']})")
        
        # Optional: Print full JSON for detailed debugging
        # print("\n--- Full JSON Result ---")
        # print(json.dumps(score_result, indent=4))
