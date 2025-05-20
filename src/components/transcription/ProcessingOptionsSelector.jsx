"use client";

import React from 'react';
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "@/components/ui/tooltip";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"; // Assuming RadioGroup is available or will be added to ui

// Minimal definition of options, ideally passed or imported from a shared constants file
const PROCESSING_OPTIONS = [
  {
    id: 'faster-whisper',
    value: 'faster-whisper',
    icon: '💻',
    title: 'Local GPU (Faster Whisper)',
    description: 'High-speed transcription using your local GPU. Best for privacy and no external API calls.',
    tooltipContent: 'Utilizes the Faster Whisper model on your computer\'s GPU. This option keeps all data local and can be very fast if you have a powerful GPU. No internet connection is needed for processing after model download.',
  },
  {
    id: 'groq',
    value: 'groq',
    icon: '☁️',
    title: 'Cloud AI (Groq)',
    description: 'Fast transcription using Groq\'s cloud API. May be quicker for some, offloads GPU work. Requires backend API key.',
    tooltipContent: 'Sends audio data to Groq\'s cloud API for transcription. This can be faster if your local GPU is not powerful or if you want to offload processing. Requires a Groq API key configured in the backend and an active internet connection.',
  },
];

const ProcessingOptionsSelector = ({ selectedOption, onOptionChange }) => {
  return (
    <TooltipProvider>
      <RadioGroup
        value={selectedOption}
        onValueChange={onOptionChange}
        className="grid grid-cols-1 md:grid-cols-2 gap-4"
      >
        {PROCESSING_OPTIONS.map((option) => (
          <Tooltip key={option.id} delayDuration={300}>
            <RadioGroupItem value={option.value} id={option.id} className="sr-only" />
            <Label htmlFor={option.id} className="cursor-pointer">
              <TooltipTrigger asChild>
                <Card
                  className={cn(
                    "hover:shadow-lg transition-shadow border-2",
                    selectedOption === option.value
                      ? "border-primary ring-2 ring-primary shadow-lg"
                      : "border-border hover:border-muted-foreground/50"
                  )}
                >
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg flex items-center">
                        <span className="mr-2 text-2xl">{option.icon}</span>
                        {option.title}
                      </CardTitle>
                      <div
                        className={cn(
                          "w-4 h-4 rounded-full border-2 flex items-center justify-center",
                          selectedOption === option.value
                            ? "bg-primary border-primary"
                            : "border-muted-foreground"
                        )}
                      >
                        {selectedOption === option.value && (
                          <div className="w-2 h-2 rounded-full bg-primary-foreground"></div>
                        )}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <CardDescription>{option.description}</CardDescription>
                  </CardContent>
                </Card>
              </TooltipTrigger>
            </Label>
            <TooltipContent side="bottom" className="max-w-xs text-sm p-2">
              <p>{option.tooltipContent}</p>
            </TooltipContent>
          </Tooltip>
        ))}
      </RadioGroup>
    </TooltipProvider>
  );
};

export default ProcessingOptionsSelector;