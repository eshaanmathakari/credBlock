import { Badge } from "@/components/ui/badge";
import { TrendingUp, Shield, Zap } from "lucide-react";

export const Hero = () => {
  return (
    <section className="bg-gradient-hero min-h-[60vh] flex items-center justify-center px-4">
      <div className="max-w-4xl mx-auto text-center">
        <Badge variant="secondary" className="mb-6 animate-fade-in">
          <Zap className="w-3 h-3 mr-1" />
          Powered by SEI Network
        </Badge>
        
        <h1 className="text-4xl md:text-6xl font-bold mb-6 animate-fade-in">
          Decentralized
          <span className="bg-gradient-primary bg-clip-text text-transparent block mt-2">
            Credit Scoring
          </span>
        </h1>
        
        <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto animate-fade-in">
          Get accurate, real-time credit scores based on your on-chain activity. 
          Leveraging AI to analyze DeFi interactions, transaction patterns, and network participation.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <div className="text-center p-6 rounded-lg bg-card shadow-soft animate-fade-in">
            <div className="w-12 h-12 bg-gradient-primary rounded-full flex items-center justify-center mx-auto mb-4">
              <Shield className="w-6 h-6 text-primary-foreground" />
            </div>
            <h3 className="font-semibold mb-2">Secure & Private</h3>
            <p className="text-sm text-muted-foreground">
              Your data stays private while providing accurate credit assessments
            </p>
          </div>
          
          <div className="text-center p-6 rounded-lg bg-card shadow-soft animate-fade-in">
            <div className="w-12 h-12 bg-gradient-success rounded-full flex items-center justify-center mx-auto mb-4">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <h3 className="font-semibold mb-2">Real-time Analysis</h3>
            <p className="text-sm text-muted-foreground">
              Instant credit scores based on current blockchain activity
            </p>
          </div>
          
          <div className="text-center p-6 rounded-lg bg-card shadow-soft animate-fade-in">
            <div className="w-12 h-12 bg-gradient-primary rounded-full flex items-center justify-center mx-auto mb-4">
              <Zap className="w-6 h-6 text-primary-foreground" />
            </div>
            <h3 className="font-semibold mb-2">AI-Powered</h3>
            <p className="text-sm text-muted-foreground">
              Advanced algorithms for precise credit score calculations
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};