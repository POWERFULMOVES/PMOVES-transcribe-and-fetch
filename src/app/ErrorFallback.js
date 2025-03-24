import React from 'react';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";

const ErrorFallback = ({ error, resetErrorBoundary, errorInfo }) => {
  const isRecoverable = error?.recoverable ?? true;

  return (
    <Alert variant="destructive" className="my-4">
      <AlertTitle>
        {error?.severity === 'fatal' ? 'Fatal Error' : 'Error'}
      </AlertTitle>
      <AlertDescription className="space-y-4">
        <div className="text-sm">
          {error?.message || 'An unexpected error occurred'}
        </div>
        
        {error?.details && (
          <div className="text-xs bg-destructive/10 p-2 rounded">
            <pre>{JSON.stringify(error.details, null, 2)}</pre>
          </div>
        )}
        
        {isRecoverable && (
          <Button 
            variant="outline" 
            onClick={resetErrorBoundary}
            className="mt-4"
          >
            Try Again
          </Button>
        )}
        
        {!isRecoverable && (
          <div className="text-sm mt-4">
            This error cannot be automatically recovered. Please check the error details and try again later.
          </div>
        )}
      </AlertDescription>
    </Alert>
  );
};

export default ErrorFallback;