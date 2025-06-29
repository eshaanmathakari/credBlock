
import React, { useState } from 'react';

export default function App() {
  const [walletConnected, setWalletConnected] = useState(false);
  const [portfolioStrategy, setPortfolioStrategy] = useState("DCA into SEI");
  const [nftTheme, setNftTheme] = useState("Cyber koi in neon seas");
  const [autoEnabled, setAutoEnabled] = useState(true);

  const connectWallet = async () => {
    const res = await fetch('http://localhost:5000/api/connect-wallet', { method: "POST" });
    const data = await res.json();
    console.log(data);
    setWalletConnected(true);
  };

  const handleMintNFT = async () => {
    const res = await fetch('http://localhost:5000/api/mint-nft', {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ theme: nftTheme })
    });
    const data = await res.json();
    console.log(data);
    alert(`Minted NFT #${data.nftId} with theme: ${data.theme}`);
  };

  const handleRebalance = async () => {
    const res = await fetch('http://localhost:5000/api/rebalance', {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ strategy: portfolioStrategy })
    });
    const data = await res.json();
    console.log(data);
    alert(data.status);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white p-6">
      <h1 className="text-4xl font-bold mb-8 text-center">
        🎨 Portfolio & Artist Agent on Sei
      </h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-gray-800 rounded-2xl shadow-xl p-6">
          <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">🔑 Sei Wallet</h2>
          <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded w-full disabled:bg-gray-600"
            onClick={connectWallet} disabled={walletConnected}>
            {walletConnected ? "Wallet Connected ✅" : "Connect Wallet"}
          </button>
        </div>
        <div className="bg-gray-800 rounded-2xl shadow-xl p-6">
          <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">📈 Portfolio Strategy</h2>
          <select className="bg-gray-700 p-3 rounded-xl w-full" value={portfolioStrategy}
            onChange={(e) => setPortfolioStrategy(e.target.value)}>
            <option>DCA into SEI</option>
            <option>Auto take profit every +25%</option>
            <option>50% SEI, 30% stable, 20% meme</option>
          </select>
          <button className="mt-4 w-full bg-green-600 hover:bg-green-700 px-4 py-2 rounded"
            onClick={handleRebalance}>Rebalance Now</button>
        </div>
        <div className="bg-gray-800 rounded-2xl shadow-xl p-6">
          <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">🎨 NFT Artist</h2>
          <input className="bg-gray-700 p-3 rounded-xl w-full mb-4" placeholder="NFT Theme (e.g., cyber koi)"
            value={nftTheme} onChange={(e) => setNftTheme(e.target.value)} />
          <button className="w-full bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded"
            onClick={handleMintNFT}>Mint New NFT</button>
        </div>
        <div className="bg-gray-800 rounded-2xl shadow-xl p-6">
          <h2 className="text-2xl font-semibold mb-4">📊 Dashboard</h2>
          <ul className="space-y-2">
            <li>Portfolio Value: $12,500 SEI + $3,000 GAIB</li>
            <li>Last NFT: "Cyber koi #7" sold for 35 SEI</li>
            <li>Weekly Gain: +18%</li>
          </ul>
          <div className="flex items-center mt-4">
            <input type="checkbox" className="h-5 w-5" checked={autoEnabled}
              onChange={() => setAutoEnabled(!autoEnabled)} />
            <span className="ml-2">Auto actions enabled</span>
          </div>
        </div>
      </div>
    </div>
  );
}
