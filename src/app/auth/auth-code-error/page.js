'use client'

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Link from 'next/link'

export default function AuthCodeError() {
  return (
    <div className="container max-w-md mx-auto mt-20">
      <Card>
        <CardHeader>
          <CardTitle className="text-destructive">Authentication Error</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">
            There was a problem authenticating your account. This could be due to:
          </p>
          <ul className="list-disc list-inside text-muted-foreground space-y-2">
            <li>An expired authentication code</li>
            <li>Invalid authentication parameters</li>
            <li>Network connectivity issues</li>
          </ul>
          <div className="flex justify-center pt-4">
            <Button asChild>
              <Link href="/">Return to Home</Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 