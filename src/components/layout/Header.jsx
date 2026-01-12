"use client";

import { ThemeToggle } from "@/components/theme-toggle";
import AuthButton from "@/components/auth/AuthButton";
import { cn } from "@/lib/utils";

export function Header({ className }) {
  return (
    <header className={cn(
      "sticky top-0 z-40 flex h-14 w-full items-center justify-end px-6",
      "bg-background/40 backdrop-blur-lg border-b border-border/40",
      className
    )}>
      <div className="flex items-center gap-4">
        {/* Connection Status / Quick Actions could go here */}
        
        <div className="flex items-center gap-2">
            <AuthButton />
            <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
