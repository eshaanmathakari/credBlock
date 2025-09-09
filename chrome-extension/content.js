// Content script for SEI Blockscout pages
(function() {
  'use strict';
  
  // API base URL - updated to production backend
  const API_BASE = 'http://44.202.188.114';
  
  // Check if we're on a wallet address page
  const addressMatch = location.pathname.match(/address\/(0x[a-fA-F0-9]{40})/);
  if (!addressMatch) return;
  
  const walletAddress = addressMatch[1];
  
  // Create overlay widget
  function createWidget() {
    const widget = document.createElement('div');
    widget.id = 'sei-credit-widget';
    widget.innerHTML = `
      <div class="credit-header">
        <span class="credit-title">🚀 SEI Credit Score</span>
        <button class="credit-close" onclick="this.parentElement.parentElement.remove()">×</button>
      </div>
      <div class="credit-content">
        <div class="credit-loading">Analyzing wallet...</div>
        <div class="credit-result" style="display: none;">
          <div class="credit-score"></div>
          <div class="credit-risk"></div>
          <div class="credit-latency"></div>
        </div>
        <div class="credit-error" style="display: none;"></div>
      </div>
    `;
    
    // Add styles
    widget.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      width: 280px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border-radius: 12px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
      z-index: 999999;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 14px;
      overflow: hidden;
      animation: slideIn 0.3s ease-out;
    `;
    
    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
      @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
      }
      
      #sei-credit-widget .credit-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 16px;
        background: rgba(255, 255, 255, 0.1);
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
      }
      
      #sei-credit-widget .credit-title {
        font-weight: 600;
        font-size: 13px;
      }
      
      #sei-credit-widget .credit-close {
        background: none;
        border: none;
        color: white;
        font-size: 18px;
        cursor: pointer;
        padding: 0;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        transition: background 0.2s;
      }
      
      #sei-credit-widget .credit-close:hover {
        background: rgba(255, 255, 255, 0.2);
      }
      
      #sei-credit-widget .credit-content {
        padding: 16px;
      }
      
      #sei-credit-widget .credit-loading {
        text-align: center;
        opacity: 0.8;
      }
      
      #sei-credit-widget .credit-score {
        font-size: 28px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 8px;
      }
      
      #sei-credit-widget .credit-risk {
        text-align: center;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        margin-bottom: 8px;
      }
      
      #sei-credit-widget .credit-risk.low {
        background: rgba(76, 175, 80, 0.3);
      }
      
      #sei-credit-widget .credit-risk.medium {
        background: rgba(255, 152, 0, 0.3);
      }
      
      #sei-credit-widget .credit-risk.high {
        background: rgba(244, 67, 54, 0.3);
      }
      
      #sei-credit-widget .credit-latency {
        text-align: center;
        font-size: 11px;
        opacity: 0.7;
      }
      
      #sei-credit-widget .credit-error {
        color: #ff6b6b;
        text-align: center;
        font-size: 12px;
      }
    `;
    document.head.appendChild(style);
    
    return widget;
  }
  
  // Fetch credit score
  async function fetchCreditScore(address) {
    const t0 = performance.now();
    
    try {
      const response = await fetch(`${API_BASE}/v1/score/${address}?chain=sei`, {
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
  
  // Update widget with results
  function updateWidget(widget, data) {
    const loading = widget.querySelector('.credit-loading');
    const result = widget.querySelector('.credit-result');
    const error = widget.querySelector('.credit-error');
    
    loading.style.display = 'none';
    error.style.display = 'none';
    result.style.display = 'block';
    
    // Score
    const scoreEl = result.querySelector('.credit-score');
    scoreEl.textContent = data.score;
    
    // Risk
    const riskEl = result.querySelector('.credit-risk');
    const riskClass = data.risk.toLowerCase().includes('low') ? 'low' : 
                     data.risk.toLowerCase().includes('high') ? 'high' : 'medium';
    riskEl.textContent = data.risk;
    riskEl.className = `credit-risk ${riskClass}`;
    
    // Latency
    const latencyEl = result.querySelector('.credit-latency');
    latencyEl.textContent = `${data.latencyMs}ms | ${Math.round(data.confidence * 100)}% confidence`;
  }
  
  // Show error in widget
  function showError(widget, message) {
    const loading = widget.querySelector('.credit-loading');
    const result = widget.querySelector('.credit-result');
    const error = widget.querySelector('.credit-error');
    
    loading.style.display = 'none';
    result.style.display = 'none';
    error.style.display = 'block';
    error.textContent = message;
  }
  
  // Main execution
  async function init() {
    // Wait a bit for page to load
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Create and add widget
    const widget = createWidget();
    document.body.appendChild(widget);
    
    // Fetch credit score
    try {
      const data = await fetchCreditScore(walletAddress);
      updateWidget(widget, data);
    } catch (err) {
      showError(widget, err.message);
    }
  }
  
  // Start the process
  init();
})();
