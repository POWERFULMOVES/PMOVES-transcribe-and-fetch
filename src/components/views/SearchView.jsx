"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

// Helper for formatted time
const formatTimeStamp = (seconds) => {
    if (!seconds && seconds !== 0) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
};

export function SearchView({ 
    searchQuery, 
    setSearchQuery, 
    searchThreshold, 
    setSearchThreshold, 
    searchResults, 
    searchLoading, 
    handleVectorSearch 
}) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
        >
            <Card className="glass-card">
                <CardHeader>
                    <CardTitle>Vector Search</CardTitle>
                    <CardDescription>Search through processed content using semantic meaning.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    {/* Search Input & Button */}
                    <div className="flex items-center gap-4">
                        <Input 
                            placeholder="Enter your search query..." 
                            value={searchQuery} 
                            onChange={(e) => setSearchQuery(e.target.value)} 
                            className="flex-grow"
                        />
                        <Button 
                            onClick={handleVectorSearch} 
                            disabled={searchLoading || !searchQuery.trim()}
                            className="bg-primary text-primary-foreground hover:bg-primary/90"
                        >
                            {searchLoading ? 'Searching...' : 'Search'}
                        </Button>
                    </div>

                    {/* Similarity Slider */}
                    <div className="space-y-2">
                        <Label htmlFor="similarity-slider">Similarity Threshold: {searchThreshold.toFixed(2)}</Label>
                        <Slider 
                            id="similarity-slider" 
                            value={[searchThreshold]} 
                            onValueChange={(value) => setSearchThreshold(value[0])} 
                            min={0} 
                            max={1} 
                            step={0.05} 
                            className="w-full"
                        />
                        <p className="text-xs text-muted-foreground">Adjust how closely results must match (higher = more strict).</p>
                    </div>

                    {/* Results Table */}
                    {searchResults.length > 0 && !searchLoading && (
                        <div className="mt-4">
                            <Label className="font-semibold">Search Results</Label>
                            <ScrollArea className="h-[500px] w-full rounded-md border border-white/10 mt-2 bg-black/40">
                                <Table>
                                    <TableHeader>
                                        <TableRow className="border-white/10 hover:bg-white/5">
                                            <TableHead className="w-[120px]">Content ID</TableHead>
                                            <TableHead className="w-[150px]">Time Range</TableHead>
                                            <TableHead>Text Snippet</TableHead>
                                            <TableHead className="w-[100px] text-right">Similarity</TableHead>
                                            <TableHead className="w-[100px]">Actions</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {searchResults.map((result, index) => (
                                            <TableRow key={result.id || index} className="border-white/10 hover:bg-white/5">
                                                <TableCell className="font-medium truncate" title={result.video_id || result.content_id}>{result.video_id || result.content_id || 'N/A'}</TableCell>
                                                <TableCell className="text-xs">{result.start_time && result.end_time ? `${formatTimeStamp(result.start_time)} - ${formatTimeStamp(result.end_time)}` : 'N/A'}</TableCell>
                                                <TableCell className="max-w-sm truncate" title={result.text || result.content}>{result.text || result.content || 'No content'}</TableCell>
                                                <TableCell className="text-right font-mono text-primary">{result.similarity ? `${(result.similarity * 100).toFixed(1)}%` : 'N/A'}</TableCell>
                                                <TableCell>
                                                    {result.watch_url && (
                                                        <Button variant="outline" size="sm" asChild className="h-8 border-white/10 hover:bg-white/10">
                                                            <a href={result.watch_url} target="_blank" rel="noopener noreferrer" title="Watch on YouTube">
                                                                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                                                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                                                </svg>
                                                            </a>
                                                        </Button>
                                                    )}
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </ScrollArea>
                        </div>
                    )}
                    
                    {searchLoading && <div className="text-center py-8 text-muted-foreground">Searching...</div>}
                    {!searchLoading && searchResults.length === 0 && searchQuery && (
                        <div className="text-center py-8 text-muted-foreground">No results found for your query. Try adjusting the threshold or query.</div>
                    )}
                </CardContent>
            </Card>
        </motion.div>
    );
}
