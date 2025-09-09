// API base URL - updated to production backend
const API_BASE = 'http://44.202.188.114';

// DOM elements
const walletInput = document.getElementById('wallet-address');
const scoreBtn = document.getElementById('score-btn');
const loading = document.getElementById('loading');
const result = document.getElementById('result');
const error = document.getElementById('error');
const scoreDisplay = document.getElementById('score-display');
const riskDisplay = document.getElementById('risk-display');
const factorsDisplay = document.getElementById('factors-display');
const latencyDisplay = document.getElementById('latency-display');

// Validate wallet address
function isValidWalletAddress(address) {
  return /^0x[a-fA-F0-9]{40}$/.test(address);
}

// Get credit score from API
async function getCreditScore(walletAddress) {
  const t0 = performance.now();
  
  try {
    const response = await fetch(`${API_BASE}/v1/score/${walletAddress}?chain=sei`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    const ms = Math.max(1, Math.round(performance.now() - t0));
    
    return { ...data, latencyMs: ms };
  } catch (err) {
    throw new Error(`Failed to fetch credit score: ${err.message}`);
  }
}

// Update UI with results
function showResult(data) {
  // Score
  scoreDisplay.textContent = data.score;
  
  // Risk level
  const riskClass = data.risk.toLowerCase().includes('low') ? 'low' : 
                   data.risk.toLowerCase().includes('high') ? 'high' : 'medium';
  riskDisplay.textContent = data.risk;
  riskDisplay.className = `risk ${riskClass}`;
  
  // Factors
  factorsDisplay.innerHTML = '';
  for (const [factor, score] of Object.entries(data.factors)) {
    const factorDiv = document.createElement('div');
    factorDiv.className = 'factor';
    factorDiv.innerHTML = `
      <span>${factor}:</span>
      <span>${score > 0 ? '+' : ''}${score}</span>
    `;
    factorsDisplay.appendChild(factorDiv);
  }
  
  // Latency
  latencyDisplay.textContent = `Response time: ${data.latencyMs}ms | Confidence: ${Math.round(data.confidence * 100)}%`;
  
  // Show result
  result.classList.add('show');
}

// Show error
function showError(message) {
  error.textContent = message;
  error.style.display = 'block';
  result.classList.remove('show');
}

// Hide error
function hideError() {
  error.style.display = 'none';
}

// Handle score button click
scoreBtn.addEventListener('click', async () => {
  const walletAddress = walletInput.value.trim();
  
  // Validate input
  if (!walletAddress) {
    showError('Please enter a wallet address');
    return;
  }
  
  if (!isValidWalletAddress(walletAddress)) {
    showError('Please enter a valid SEI wallet address (0x...)');
    return;
  }
  
  // Reset UI
  hideError();
  result.classList.remove('show');
  loading.style.display = 'block';
  scoreBtn.disabled = true;
  
  try {
    const data = await getCreditScore(walletAddress);
    showResult(data);
  } catch (err) {
    showError(err.message);
  } finally {
    loading.style.display = 'none';
    scoreBtn.disabled = false;
  }
});

// Handle Enter key
walletInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    scoreBtn.click();
  }
});

// Auto-fill from active tab if on Blockscout
chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
  const url = tabs[0]?.url;
  if (url && url.includes('sei.blockscout.com/address/')) {
    const match = url.match(/address\/(0x[a-fA-F0-9]{40})/);
    if (match) {
      walletInput.value = match[1];
    }
  }
});

// Focus input on popup open
walletInput.focus();
