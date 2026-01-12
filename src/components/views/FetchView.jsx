"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import ReactMarkdown from 'react-markdown';
import { ACTIONS } from "@/app/reducers/transcriptionReducer";

export function FetchView({ state, dispatch, handleFetchContent }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
        >
            <Card className="glass-card">
                <CardHeader>
                    <CardTitle>Fetch & Process Web Content</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                    {/* URL Input */}
                    <div className="space-y-2">
                        <Label htmlFor="fetch-url">URL to Fetch</Label>
                        <Input 
                            id="fetch-url" 
                            placeholder="Enter URL (e.g., https://example.com/article)" 
                            value={state.fetchUrl} 
                            onChange={(e) => dispatch({ type: ACTIONS.SET_FETCH_URL, payload: e.target.value })} 
                        />
                    </div>

                    {/* Advanced Options Accordion */}
                    <Accordion type="single" collapsible className="w-full border border-white/5 rounded-md">
                        <AccordionItem value="advanced-options">
                            <AccordionTrigger className="px-4 py-2 text-sm font-medium">Advanced Fetch Options</AccordionTrigger>
                            <AccordionContent className="p-4 space-y-4 bg-black/20">
                                <div className="space-y-2">
                                    <Label htmlFor="target-selector">Target CSS Selector (Optional)</Label>
                                    <Input 
                                        id="target-selector" 
                                        placeholder="e.g., article, .main-content, #content-body" 
                                        value={state.targetSelector} 
                                        onChange={(e) => dispatch({ type: ACTIONS.SET_TARGET_SELECTOR, payload: e.target.value })} 
                                    />
                                    <p className="text-xs text-muted-foreground">Extract content only from elements matching this selector.</p>
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="exclude-selector">Exclude CSS Selectors (Optional)</Label>
                                    <Input 
                                        id="exclude-selector" 
                                        placeholder="e.g., nav, footer, .ad-banner, script" 
                                        value={state.excludedSelector} 
                                        onChange={(e) => dispatch({ type: ACTIONS.SET_EXCLUDED_SELECTOR, payload: e.target.value })} 
                                    />
                                    <p className="text-xs text-muted-foreground">Remove elements matching these selectors (comma-separated).</p>
                                </div>
                            </AccordionContent>
                        </AccordionItem>
                    </Accordion>

                    {/* Fetch Button */}
                    <Button 
                        onClick={handleFetchContent} 
                        disabled={state.loading || !state.fetchUrl.trim()} 
                        className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-bold py-2 px-4 rounded transition-all hover-lift"
                    >
                        {state.loading ? 'Fetching...' : 'Fetch & Upsert Content'}
                    </Button>

                    {/* Results Display Area */}
                    <div className="mt-4">
                        <Label className="font-semibold">Fetched Content (Markdown)</Label>
                        <ScrollArea className="h-[400px] w-full rounded-md border border-white/10 p-4 mt-2 bg-black/40">
                            {state.fetchResult?.markdown_content ? (
                                <div className="prose prose-sm dark:prose-invert max-w-none">
                                    <ReactMarkdown components={{ a: ({ node, ...props }) => (<a className="text-primary hover:underline" target="_blank" rel="noopener noreferrer" {...props} />), }}>
                                        {typeof state.fetchResult.markdown_content === 'object' ? `\`\`\`json\n${JSON.stringify(state.fetchResult.markdown_content, null, 2)}\n\`\`\`` : state.fetchResult.markdown_content}
                                    </ReactMarkdown>
                                </div>
                            ) : (
                                <div className="text-center py-8 text-muted-foreground">
                                    {state.loading ? "Fetching..." : "Fetched content will appear here."}
                                </div>
                            )}
                            <ScrollBar orientation="vertical" />
                        </ScrollArea>
                    </div>
                </CardContent>
            </Card>
        </motion.div>
    );
}
