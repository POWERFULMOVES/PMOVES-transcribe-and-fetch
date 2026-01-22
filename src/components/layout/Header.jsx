"use client";

import { ThemeToggle } from "@/components/theme-toggle";
import AuthButton from "@/components/auth/AuthButton";
import { MobileMenuButton } from "@/components/layout/Sidebar";
import { cn } from "@/lib/utils";

export function Header({ className }) {
  return (
    <header className={cn(
      "sticky top-0 z-40 flex h-14 w-full items-center justify-between px-4 md:px-6",
      "bg-background/40 backdrop-blur-lg border-b border-border/40",
      className
    )}>
      {/* Mobile menu button - only visible on small screens */}
      <div className="flex items-center gap-2">
        <MobileMenuButton />
        {/* Mobile branding */}
        <div className="md:hidden flex items-center gap-2">
          <div className="h-6 w-6 rounded bg-primary/20 flex items-center justify-center">
            <span className="text-primary font-bold text-sm">P</span>
          </div>
          <span className="font-bold text-base tracking-tight">PMOVES</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
            <AuthButton />
            <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
