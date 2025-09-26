import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorBoundaryState {
    hasError: boolean;
    error: Error | null;
}

interface ErrorBoundaryProps {
    children: React.ReactNode;
}

class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
    constructor(props: ErrorBoundaryProps) {
        super(props);
        this.state = { hasError: false, error: null};
    }

    static getDerivedStateFromError(error: Error): ErrorBoundaryState {
        return { hasError: true, error};
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo){
        console.error('Error Boundary caught an error:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen flex items-center justify-center bg-background">
                <div className="text-center space-y-4">
                    <AlertTriangle className="h-16 w-16 text-destructive mx-auto" />
                    <h2 className="text-2xl font-bold text-foreground">Something went wrong</h2>
                    <p className="text-muted-foreground">
                    {this.state.error?.message || 'An unexpected error occurred'}
                    </p>
                    <button
                    onClick={() => this.setState({ hasError: false, error: null })}
                    className="inline-flex items-center px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
                    >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Try Again
                    </button>
                </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;