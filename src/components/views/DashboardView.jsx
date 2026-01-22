"use client";

import { motion } from "framer-motion";
import { ArrowRight, Mic, Globe, Download } from "lucide-react";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      type: "spring",
      stiffness: 100
    }
  }
};

export default function DashboardView({ onViewChange }) {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="flex flex-col gap-8"
    >
      {/* Hero Section */}
      <motion.div variants={itemVariants} className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary/10 via-background to-accent/5 p-8 border border-white/5">
        <div className="relative z-10 flex flex-col gap-4 max-w-2xl">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-white mb-2">
            AI-Powered <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">Media Intelligence</span>
          </h1>
          <p className="text-lg text-muted-foreground leading-relaxed">
            Transcribe YouTube videos, fetch web content, and analyze data with advanced vector search.
            Your all-in-one research power tool.
          </p>
          <div className="flex gap-4 mt-4">
             <button 
                onClick={() => onViewChange("transcribe")}
                className="group flex items-center gap-2 bg-primary text-primary-foreground px-6 py-3 rounded-xl font-semibold hover:bg-primary/90 transition-all hover-lift"
             >
                Start Transcribing <ArrowRight size={18} className="translate-x-0 group-hover:translate-x-1 transition-transform" />
             </button>
             <button 
                onClick={() => onViewChange("search")}
                className="flex items-center gap-2 bg-secondary/50 text-foreground px-6 py-3 rounded-xl font-medium border border-white/5 hover:bg-secondary/80 transition-all"
             >
                Search Knowledge Base
             </button>
          </div>
        </div>
        
        {/* Abstract Background Decoration */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-primary/20 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-accent/10 rounded-full blur-3xl translate-y-1/2 -translate-x-1/4" />
      </motion.div>

      {/* Quick Actions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <QuickActionCard 
            title="Transcribe & Analyze"
            description="Convert YouTube videos to text with timestamped segments."
            icon={Mic}
            color="text-indigo-400"
            onClick={() => onViewChange("transcribe")}
            delay={0.2}
        />
        <QuickActionCard 
            title="Fetch Web Content"
            description="Scrape and process webpages into clean Markdown for analysis."
            icon={Globe}
            color="text-teal-400"
            onClick={() => onViewChange("fetch")}
            delay={0.3}
        />
        <QuickActionCard 
            title="Download Media"
            description="Securely download video and audio from various sources."
            icon={Download}
            color="text-purple-400"
            onClick={() => onViewChange("download")}
            delay={0.4}
        />
      </div>
    </motion.div>
  );
}

function QuickActionCard({ title, description, icon: Icon, color, onClick, delay }) {
    return (
        <motion.div 
            variants={itemVariants}
            className="group cursor-pointer glass-card p-6 rounded-2xl hover:bg-card/80 transition-colors"
            onClick={onClick}
        >
            <div className={`mb-4 inline-flex p-3 rounded-xl bg-background/50 ring-1 ring-white/10 ${color}`}>
                <Icon size={28} />
            </div>
            <h3 className="text-xl font-bold text-foreground mb-2 group-hover:text-primary transition-colors">{title}</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
        </motion.div>
    )
}
