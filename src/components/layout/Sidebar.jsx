"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Mic, Globe, Download, Database, Sparkles, Menu, X, LayoutDashboard } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
  SheetTitle,
} from "@/components/ui/sheet";

const sidebarVariants = {
  expanded: { width: 240 },
  collapsed: { width: 80 }
};

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/transcribe", label: "Transcribe", icon: Mic },
  { href: "/fetch", label: "Fetch Content", icon: Globe },
  { href: "/download", label: "Download", icon: Download },
  { href: "/upserter", label: "Upserter", icon: Database },
  { href: "/vector-search", label: "Vector Search", icon: Sparkles },
];

// Shared navigation component for both desktop and mobile
function NavigationItems({ isExpanded = true, onNavigate }) {
  const pathname = usePathname();

  return (
    <nav className="flex-1 space-y-2 p-3">
      {navItems.map((item) => {
        const isActive = pathname === item.href;
        const Icon = item.icon;

        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={onNavigate}
            className={cn(
              "group flex items-center gap-3 rounded-lg px-3 py-2.5 transition-all duration-200",
              isActive
                ? "bg-primary/10 text-primary shadow-sm shadow-primary/5"
                : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground"
            )}
          >
            <div className={cn(
                "relative flex items-center justify-center transition-colors",
                isActive ? "text-primary" : "group-hover:text-primary"
            )}>
              <Icon size={22} strokeWidth={isActive ? 2.5 : 2} />
              {isActive && (
                  <motion.div
                      layoutId="active-glow"
                      className="absolute inset-0 rounded-full bg-primary/20 blur-md"
                      transition={{ duration: 0.2 }}
                  />
              )}
            </div>

            {isExpanded && (
              <span className="overflow-hidden whitespace-nowrap font-medium">
                {item.label}
              </span>
            )}

            {/* Active Indicator Line */}
            {isActive && isExpanded && (
                <motion.div
                    layoutId="active-indicator"
                    className="absolute left-0 h-6 w-1 rounded-r-full bg-primary"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                />
            )}
          </Link>
        );
      })}
    </nav>
  );
}

// Mobile hamburger menu button - shown in header area on mobile
export function MobileMenuButton() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <SheetTrigger asChild>
        <button
          className="md:hidden p-2 rounded-lg hover:bg-secondary/50 text-muted-foreground hover:text-foreground transition-colors"
          aria-label="Open navigation menu"
        >
          <Menu size={24} />
        </button>
      </SheetTrigger>
      <SheetContent side="left" className="w-64 p-0 bg-card/95 backdrop-blur-xl border-r border-border/50">
        <SheetTitle className="sr-only">Navigation Menu</SheetTitle>

        {/* Mobile Sidebar Header */}
        <div className="flex h-14 items-center gap-2 px-4 border-b border-border/50">
          <div className="h-6 w-6 rounded bg-primary/20 flex items-center justify-center">
            <span className="text-primary font-bold">P</span>
          </div>
          <span className="font-bold text-lg tracking-tight">PMOVES</span>
        </div>

        {/* Navigation Items */}
        <NavigationItems isExpanded={true} onNavigate={() => setIsOpen(false)} />

        {/* Footer */}
        <div className="p-4 border-t border-border/50">
          <div className="text-xs text-muted-foreground text-center">
            v0.1.0-beta
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}

// Desktop Sidebar - hidden on mobile
export function Sidebar() {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <motion.div
      initial="expanded"
      animate={isExpanded ? "expanded" : "collapsed"}
      variants={sidebarVariants}
      className={cn(
        "relative hidden h-screen flex-col border-r bg-card/50 backdrop-blur-xl md:flex z-50 transition-all duration-300 ease-in-out",
        "border-border/50 shadow-2xl"
      )}
    >
      {/* Toggle Button */}
      <div className="flex h-14 items-center justify-between px-4 border-b border-border/50">
        <motion.div
            initial={{ opacity: 1 }}
            animate={{ opacity: isExpanded ? 1 : 0 }}
            className="flex items-center gap-2 overflow-hidden whitespace-nowrap"
        >
            <div className="h-6 w-6 rounded bg-primary/20 flex items-center justify-center">
                <span className="text-primary font-bold">P</span>
            </div>
            <span className="font-bold text-lg tracking-tight">PMOVES</span>
        </motion.div>

        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="p-1.5 rounded-md hover:bg-secondary/80 text-muted-foreground hover:text-foreground transition-colors"
          aria-label={isExpanded ? "Collapse sidebar" : "Expand sidebar"}
        >
          {isExpanded ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Navigation */}
      <NavigationItems isExpanded={isExpanded} />

      {/* Footer Info */}
      <div className="p-4 border-t border-border/50">
           <motion.div
            animate={{ opacity: isExpanded ? 1 : 0 }}
             className={cn("text-xs text-muted-foreground text-center", !isExpanded && "hidden")}
           >
             v0.1.0-beta
           </motion.div>
      </div>
    </motion.div>
  );
}
