import { useState } from "react";
import { Hero } from "@/components/Hero";
import { WalletInput } from "@/components/WalletInput";
import { CreditScoreDisplay } from "@/components/CreditScoreDisplay";
import { Chatbot } from "@/components/Chatbot";
import { useToast } from "@/hooks/use-toast";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";

const fallbackBase = typeof window !== "undefined" ? window.location.origin : "http://localhost:8000";
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || fallbackBase).replace(/\/$/, "");

// Real API call to backend; base URL is configurable via VITE_API_BASE_URL
const fetchCreditScore = async (walletAddress: string, chain: string = 'sei') => {
  const t0 = performance.now();
  
  const apiUrl = `${API_BASE_URL}/v1/score/${walletAddress}?chain=${chain}`;
  
  const response = await fetch(apiUrl, {
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
  
  // Transform the data to match the expected format
  return {
    score: data.score,
    accuracy: Math.round(data.confidence * 100),
    grade: data.score >= 850 ? 'A+' : data.score >= 700 ? 'A' : data.score >= 500 ? 'B' : 'C',
    riskLevel: data.risk.toLowerCase().includes('low') ? 'low' : 
               data.risk.toLowerCase().includes('high') ? 'high' : 'medium',
    factors: {
      transactionHistory: data.factors['Tx Activity'] || 0,
      liquidityProvision: data.factors['Balances'] || 0,
      defiInteractions: data.factors['DeFi Extras'] || 0,
      networkParticipation: data.factors['Account Age'] || 0,
      staking: data.factors['Staking'] || 0,
      governance: data.factors['Governance'] || 0,
    },
    walletAddress: data.wallet,
    chain: data.chain,
    latencyMs: ms,
    confidence: data.confidence,
    risk: data.risk,
    modelVersion: data.model_version,
  };
};

const Index = () => {
  const [creditData, setCreditData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedChain, setSelectedChain] = useState('sei');
  const { toast } = useToast();

  const handleWalletSubmit = async (walletAddress: string) => {
    setIsLoading(true);
    setCreditData(null);
    
    try {
      const data = await fetchCreditScore(walletAddress, selectedChain);
      setCreditData(data);
      toast({
        title: "Credit Score Retrieved",
        description: `Score: ${data.score} (${data.latencyMs}ms) - ${walletAddress.slice(0, 6)}...${walletAddress.slice(-4)}`,
      });
    } catch (error) {
      console.error('Error fetching credit score:', error);
      toast({
        title: "Error",
        description: "Failed to fetch credit score. Please check if the backend is running.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Hero />
      
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          {!creditData ? (
            <div className="space-y-6">
              {/* Chain Selector */}
              <div className="flex justify-center">
                <div className="flex items-center space-x-4">
                  <label className="text-sm font-medium text-muted-foreground">Select Blockchain:</label>
                  <Select value={selectedChain} onValueChange={setSelectedChain}>
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="sei">SEI</SelectItem>
                      <SelectItem value="eth">Ethereum</SelectItem>
                      <SelectItem value="sol">Solana</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <WalletInput onSubmit={handleWalletSubmit} isLoading={isLoading} />
            </div>
          ) : (
            <div className="space-y-8">
              {/* Chain Badge */}
              <div className="flex justify-center">
                <Badge variant="outline" className="text-sm">
                  {creditData.chain?.toUpperCase() || selectedChain.toUpperCase()}
                </Badge>
              </div>
              
              <CreditScoreDisplay data={creditData} />
              <div className="text-center space-y-4">
                <div className="text-sm text-muted-foreground">
                  Response time: {creditData.latencyMs}ms | Confidence: {Math.round(creditData.confidence * 100)}%
                  {creditData.modelVersion && ` | Model: ${creditData.modelVersion}`}
                </div>
                <button
                  onClick={() => setCreditData(null)}
                  className="text-primary hover:text-primary/80 font-medium transition-colors"
                >
                  Check Another Wallet
                </button>
              </div>
            </div>
          )}
        </div>
      </section>
      
      <Chatbot />
    </div>
  );
};

export default Index;
