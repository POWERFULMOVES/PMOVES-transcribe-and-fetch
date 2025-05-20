'use client';

import React from 'react';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

const FetchProgressTracker = ({ progressPercent, progressMessage, onCancel }) => {
  if (progressPercent === null && !progressMessage) {
    return null;
  }

  return (
    <Card className="w-full max-w-md mt-4">
      <CardHeader>
        <CardTitle>Fetching Content</CardTitle>
      </CardHeader>
      <CardContent>
        {progressMessage && (
          <p className="mb-2 text-sm text-muted-foreground">
            Status: {progressMessage}
          </p>
        )}
        {typeof progressPercent === 'number' && (
          <Progress value={progressPercent} className="w-full" />
        )}
        {typeof progressPercent === 'number' && (
          <p className="mt-2 text-xs text-center text-muted-foreground">
            {progressPercent}%
          </p>
        )}
      </CardContent>
      <CardFooter className="flex justify-end">
        <Button variant="outline" onClick={onCancel}>
          Cancel
        </Button>
      </CardFooter>
    </Card>
  );
};

export default FetchProgressTracker;