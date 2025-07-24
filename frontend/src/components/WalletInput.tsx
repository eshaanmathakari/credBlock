import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Search, Wallet } from "lucide-react";

interface WalletInputProps {
  onSubmit: (walletAddress: string) => void;
  isLoading?: boolean;
}

export const WalletInput = ({ onSubmit, isLoading }: WalletInputProps) => {
  const [walletAddress, setWalletAddress] = useState("");
  const [error, setError] = useState("");

  const validateWalletAddress = (address: string) => {
    // Basic validation for wallet address format
    const ethRegex = /^0x[a-fA-F0-9]{40}$/;
    const solanaRegex = /^[A-Za-z0-9]{32,44}$/;
    
    if (!address) {
      return "Wallet address is required";
    }
    
    if (!ethRegex.test(address) && !solanaRegex.test(address)) {
      return "Please enter a valid wallet address";
    }
    
    return "";
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const validationError = validateWalletAddress(walletAddress);
    if (validationError) {
      setError(validationError);
      return;
    }
    
    setError("");
    onSubmit(walletAddress);
  };

  return (
    <Card className="w-full max-w-md mx-auto shadow-soft animate-fade-in">
      <CardHeader className="text-center">
        <div className="mx-auto w-12 h-12 bg-gradient-primary rounded-full flex items-center justify-center mb-4">
          <Wallet className="w-6 h-6 text-primary-foreground" />
        </div>
        <CardTitle className="text-2xl font-bold">Check Credit Score</CardTitle>
        <CardDescription>
          Enter your wallet address to get your SEI Network credit score
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Input
              type="text"
              placeholder="0x... or wallet address"
              value={walletAddress}
              onChange={(e) => setWalletAddress(e.target.value)}
              className={`transition-all duration-300 ${error ? 'border-destructive' : ''}`}
              disabled={isLoading}
            />
            {error && (
              <p className="text-sm text-destructive animate-fade-in">{error}</p>
            )}
          </div>
          
          <Button 
            type="submit" 
            className="w-full bg-gradient-primary hover:shadow-glow transition-all duration-300"
            disabled={isLoading}
          >
            {isLoading ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin" />
                Analyzing...
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Search className="w-4 h-4" />
                Get Credit Score
              </div>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};