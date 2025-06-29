
const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

app.post('/api/connect-wallet', (req, res) => {
  console.log("Connecting to Sei wallet...");
  res.json({ status: "Wallet connected ✅", wallet: "sei1example..." });
});

app.post('/api/mint-nft', (req, res) => {
  const { theme } = req.body;
  console.log(`Minting NFT with theme: ${theme}`);
  res.json({ status: "NFT minted", nftId: Math.floor(Math.random()*1000), theme });
});

app.post('/api/rebalance', (req, res) => {
  const { strategy } = req.body;
  console.log(`Rebalancing portfolio using strategy: ${strategy}`);
  res.json({ status: "Portfolio rebalanced with strategy: " + strategy });
});

const PORT = 5000;
app.listen(PORT, () => {
  console.log(`🚀 Backend running on http://localhost:${PORT}`);
});
