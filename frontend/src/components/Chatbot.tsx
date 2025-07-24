import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageCircle, X, Send, Bot, User } from "lucide-react";
import { cn } from "@/lib/utils";

interface Message {
  id: string;
  text: string;
  isBot: boolean;
  timestamp: Date;
}

const predefinedResponses = {
  greeting: [
    "hello", "hi", "hey", "good morning", "good afternoon", "good evening"
  ],
  creditScore: [
    "credit score", "score", "rating", "credit rating", "how does scoring work"
  ],
  seiNetwork: [
    "sei network", "sei", "what is sei", "blockchain", "network"
  ],
  howItWorks: [
    "how it works", "how does it work", "process", "algorithm", "calculation"
  ],
  accuracy: [
    "accuracy", "reliable", "trust", "precise", "how accurate"
  ],
  wallet: [
    "wallet", "address", "connect wallet", "supported wallets"
  ],
  privacy: [
    "privacy", "secure", "safety", "data protection", "private"
  ],
  fees: [
    "cost", "fee", "price", "payment", "free"
  ]
};

const responses = {
  greeting: "Hello! I'm here to help you with questions about SEI Network credit scoring. How can I assist you today?",
  creditScore: "Our credit scoring system analyzes your on-chain activity including transaction history, DeFi interactions, liquidity provision, and network participation. Scores range from 0-1000 with higher scores indicating better creditworthiness.",
  seiNetwork: "SEI Network is a high-performance blockchain optimized for DeFi applications. Our platform leverages SEI's fast transaction speeds and low costs to provide real-time credit scoring based on your blockchain activity.",
  howItWorks: "Simply enter your wallet address and our AI analyzes your on-chain activity across multiple factors: transaction patterns, DeFi protocol usage, liquidity provision history, and network participation. The analysis takes about 2-3 seconds to complete.",
  accuracy: "Our credit scores have 80-100% accuracy thanks to advanced AI algorithms that analyze comprehensive on-chain data. The accuracy percentage is displayed with each score to give you confidence in the results.",
  wallet: "We support Ethereum (0x...) and Solana wallet addresses. Simply paste your public wallet address - no connection or private keys required. Your data remains completely private.",
  privacy: "Your privacy is our priority. We only analyze public blockchain data and never store your personal information. No wallet connection is required - just enter your public address.",
  fees: "Our basic credit score service is completely free! You can check any wallet address without any charges or registration required.",
  default: "I'd be happy to help! I can answer questions about SEI Network, credit scoring, how our platform works, privacy, supported wallets, and more. What would you like to know?"
};

export const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hi! I'm your SEI Network assistant. I can help answer questions about credit scoring, how our platform works, privacy, and more. What would you like to know?",
      isBot: true,
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (scrollAreaRef.current) {
      const scrollElement = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollElement) {
        scrollElement.scrollTop = scrollElement.scrollHeight;
      }
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const findBestResponse = (userMessage: string): string => {
    const lowerMessage = userMessage.toLowerCase();
    
    for (const [category, keywords] of Object.entries(predefinedResponses)) {
      if (keywords.some(keyword => lowerMessage.includes(keyword))) {
        return responses[category as keyof typeof responses];
      }
    }
    
    return responses.default;
  };

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      isBot: false,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText("");
    setIsTyping(true);

    // Simulate typing delay
    setTimeout(() => {
      const botResponse = findBestResponse(inputText);
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: botResponse,
        isBot: true,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
      setIsTyping(false);
    }, 1000 + Math.random() * 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <>
      {/* Floating Chat Button */}
      <Button
        onClick={() => setIsOpen(true)}
        className={cn(
          "fixed bottom-6 right-6 w-14 h-14 rounded-full shadow-glow bg-gradient-primary hover:shadow-xl transition-all duration-300 z-50",
          isOpen && "hidden"
        )}
        size="icon"
      >
        <MessageCircle className="w-6 h-6" />
      </Button>

      {/* Chat Window */}
      {isOpen && (
        <Card className="fixed bottom-6 right-6 w-96 h-[500px] shadow-xl z-50 animate-fade-in">
          <CardHeader className="bg-gradient-primary text-primary-foreground rounded-t-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Bot className="w-5 h-5" />
                <CardTitle className="text-lg">SEI Assistant</CardTitle>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsOpen(false)}
                className="text-primary-foreground hover:bg-white/20 h-8 w-8"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          </CardHeader>

          <CardContent className="p-0 flex flex-col h-[420px]">
            {/* Messages */}
            <ScrollArea ref={scrollAreaRef} className="flex-1 p-4">
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={cn(
                      "flex gap-2 animate-fade-in",
                      message.isBot ? "justify-start" : "justify-end"
                    )}
                  >
                    {message.isBot && (
                      <div className="w-8 h-8 bg-gradient-primary rounded-full flex items-center justify-center flex-shrink-0">
                        <Bot className="w-4 h-4 text-primary-foreground" />
                      </div>
                    )}
                    <div
                      className={cn(
                        "max-w-[80%] p-3 rounded-lg text-sm",
                        message.isBot
                          ? "bg-muted text-foreground"
                          : "bg-gradient-primary text-primary-foreground"
                      )}
                    >
                      {message.text}
                    </div>
                    {!message.isBot && (
                      <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center flex-shrink-0">
                        <User className="w-4 h-4 text-secondary-foreground" />
                      </div>
                    )}
                  </div>
                ))}
                
                {isTyping && (
                  <div className="flex gap-2 justify-start animate-fade-in">
                    <div className="w-8 h-8 bg-gradient-primary rounded-full flex items-center justify-center flex-shrink-0">
                      <Bot className="w-4 h-4 text-primary-foreground" />
                    </div>
                    <div className="bg-muted p-3 rounded-lg">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" />
                        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>

            {/* Input */}
            <div className="border-t p-4">
              <div className="flex gap-2">
                <Input
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me about SEI Network..."
                  className="flex-1"
                  disabled={isTyping}
                />
                <Button
                  onClick={handleSendMessage}
                  size="icon"
                  disabled={!inputText.trim() || isTyping}
                  className="bg-gradient-primary hover:shadow-glow"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </>
  );
};