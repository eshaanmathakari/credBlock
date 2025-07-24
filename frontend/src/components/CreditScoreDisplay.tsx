import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { TrendingUp, Shield, AlertCircle, CheckCircle } from "lucide-react";

interface CreditScoreData {
  score: number;
  accuracy: number;
  grade: string;
  riskLevel: 'low' | 'medium' | 'high';
  factors: {
    transactionHistory: number;
    liquidityProvision: number;
    defiInteractions: number;
    networkParticipation: number;
  };
  walletAddress: string;
}

interface CreditScoreDisplayProps {
  data: CreditScoreData;
}

export const CreditScoreDisplay = ({ data }: CreditScoreDisplayProps) => {
  const getScoreColor = (score: number) => {
    if (score >= 750) return "bg-gradient-success";
    if (score >= 650) return "bg-gradient-primary";
    return "bg-destructive";
  };

  const getRiskIcon = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low':
        return <CheckCircle className="w-5 h-5 text-secondary" />;
      case 'medium':
        return <AlertCircle className="w-5 h-5 text-primary" />;
      default:
        return <AlertCircle className="w-5 h-5 text-destructive" />;
    }
  };

  const formatWalletAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6 animate-fade-in">
      {/* Main Score Card */}
      <Card className="shadow-soft">
        <CardHeader className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <Shield className="w-5 h-5 text-primary" />
            <CardTitle>SEI Network Credit Score</CardTitle>
          </div>
          <CardDescription>
            Wallet: {formatWalletAddress(data.walletAddress)}
          </CardDescription>
        </CardHeader>
        <CardContent className="text-center">
          <div className="relative">
            <div className={`w-32 h-32 mx-auto rounded-full ${getScoreColor(data.score)} flex items-center justify-center shadow-glow animate-pulse-glow`}>
              <div className="text-center">
                <div className="text-3xl font-bold text-white">{data.score}</div>
                <div className="text-sm text-white/80">/{1000}</div>
              </div>
            </div>
            <Badge variant="secondary" className="absolute -bottom-2 left-1/2 transform -translate-x-1/2">
              Grade {data.grade}
            </Badge>
          </div>
          
          <div className="mt-6 flex items-center justify-center gap-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-primary" />
              <span className="text-sm font-medium">Accuracy: {data.accuracy}%</span>
            </div>
            <div className="flex items-center gap-2">
              {getRiskIcon(data.riskLevel)}
              <span className="text-sm font-medium capitalize">{data.riskLevel} Risk</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Score Factors */}
      <Card className="shadow-soft">
        <CardHeader>
          <CardTitle className="text-lg">Score Breakdown</CardTitle>
          <CardDescription>
            Factors contributing to your credit score
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-medium">Transaction History</span>
                <span className="text-sm text-muted-foreground">{data.factors.transactionHistory}%</span>
              </div>
              <Progress value={data.factors.transactionHistory} className="h-2" />
            </div>
            
            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-medium">Liquidity Provision</span>
                <span className="text-sm text-muted-foreground">{data.factors.liquidityProvision}%</span>
              </div>
              <Progress value={data.factors.liquidityProvision} className="h-2" />
            </div>
            
            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-medium">DeFi Interactions</span>
                <span className="text-sm text-muted-foreground">{data.factors.defiInteractions}%</span>
              </div>
              <Progress value={data.factors.defiInteractions} className="h-2" />
            </div>
            
            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-medium">Network Participation</span>
                <span className="text-sm text-muted-foreground">{data.factors.networkParticipation}%</span>
              </div>
              <Progress value={data.factors.networkParticipation} className="h-2" />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};