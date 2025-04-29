import React from "react"
import { cn } from "@/lib/utils"

const badgeStyles = {
  base: "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  variants: {
    default: "border-transparent bg-[hsl(var(--page-accent))] text-[hsl(var(--background))] hover:bg-[hsl(var(--page-accent)/0.8)]",
    secondary: "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
    destructive: "border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80",
    outline: "text-foreground"
  }
}

function Badge({
  className,
  variant = "default",
  ...props
}) {
  const variantStyle = badgeStyles.variants[variant] || badgeStyles.variants.default
  
  return (
    <div 
      className={cn(badgeStyles.base, variantStyle, className)} 
      {...props} 
    />
  )
}

export { Badge } 