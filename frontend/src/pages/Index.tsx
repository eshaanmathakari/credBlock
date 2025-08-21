import { useState } from "react";
import { Hero } from "@/components/Hero";
import { WalletInput } from "@/components/WalletInput";
import { CreditScoreDisplay } from "@/components/CreditScoreDisplay";
import { Chatbot } from "@/components/Chatbot";
import { useToast } from "@/hooks/use-toast";

// Real API call to Flask backend
const fetchCreditScore = async (walletAddress: string) => {
  const t0 = performance.now();
  
  // Use the Flask backend API
  const response = await fetch(`http://localhost:5000/score/${walletAddress}`, {
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
    latencyMs: ms,
    confidence: data.confidence,
    risk: data.risk,
  };
};

const Index = () => {
  const [creditData, setCreditData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleWalletSubmit = async (walletAddress: string) => {
    setIsLoading(true);
    setCreditData(null);
    
    try {
      const data = await fetchCreditScore(walletAddress);
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
            <WalletInput onSubmit={handleWalletSubmit} isLoading={isLoading} />
          ) : (
            <div className="space-y-8">
              <CreditScoreDisplay data={creditData} />
              <div className="text-center space-y-4">
                <div className="text-sm text-muted-foreground">
                  Response time: {creditData.latencyMs}ms | Confidence: {Math.round(creditData.confidence * 100)}%
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
