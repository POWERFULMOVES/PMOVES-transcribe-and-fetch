import React from 'react';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Alert variant="destructive">
          <AlertTitle>Something went wrong</AlertTitle>
          <AlertDescription>
            {this.state.error?.message || 'An unexpected error occurred'}
            <Button
              className="mt-4"
              onClick={() => {
                this.setState({ hasError: false, error: null });
                window.location.reload();
              }}
            >
              Retry
            </Button>
          </AlertDescription>
        </Alert>
      );
    }

    return this.props.children;
  }
}