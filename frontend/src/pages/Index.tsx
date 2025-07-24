import { useState } from "react";
import { Hero } from "@/components/Hero";
import { WalletInput } from "@/components/WalletInput";
import { CreditScoreDisplay } from "@/components/CreditScoreDisplay";
import { Chatbot } from "@/components/Chatbot";
import { useToast } from "@/hooks/use-toast";

// Mock API call - replace with actual SEI Network API
const fetchCreditScore = async (walletAddress: string) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // Mock credit score data
  return {
    score: Math.floor(Math.random() * 300) + 600, // 600-900 range
    accuracy: Math.floor(Math.random() * 20) + 80, // 80-100% range
    grade: ['A+', 'A', 'A-', 'B+', 'B'][Math.floor(Math.random() * 5)],
    riskLevel: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)] as 'low' | 'medium' | 'high',
    factors: {
      transactionHistory: Math.floor(Math.random() * 40) + 60,
      liquidityProvision: Math.floor(Math.random() * 40) + 40,
      defiInteractions: Math.floor(Math.random() * 50) + 30,
      networkParticipation: Math.floor(Math.random() * 60) + 40,
    },
    walletAddress,
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
        description: `Successfully analyzed wallet: ${walletAddress.slice(0, 6)}...${walletAddress.slice(-4)}`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch credit score. Please try again.",
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
              <div className="text-center">
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
