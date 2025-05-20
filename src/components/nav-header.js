"use client";

import Link from 'next/link';
import Image from 'next/image';
import { ThemeToggle } from "@/components/theme-toggle";
import { permanentMarker } from '@/app/fonts';
import AuthButton from './auth/AuthButton';

export function NavHeader() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex items-center">
          <Link href="/" className="flex items-center gap-2">
            <div className="relative h-8 w-auto">
              <Image
                src="/images/pmoves.svg"
                alt="PMOVES Logo"
                width={400}
                height={139}
                className="logo-glow logo-text"
                priority
                style={{
                  height: '100%',
                  width: 'auto',
                  objectFit: 'contain'
                }}
              />
            </div>
            <span className={`${permanentMarker.className} text-xl`}>
              PMoves Transcriber
            </span>
          </Link>
        </div>
        <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
          <nav className="flex items-center space-x-6">
            <Link
              href="/"
              className="transition-colors hover:text-foreground/80 text-foreground/60"
            >
              Transcribe
            </Link>
            <Link
              href="/fetch"
              className="transition-colors hover:text-foreground/80 text-foreground/60"
            >
              Fetch Content
            </Link>
            <Link
              href="/download"
              className="transition-colors hover:text-foreground/80 text-foreground/60"
            >
              Download
            </Link>
            <Link
              href="/upserter"
              className="transition-colors hover:text-foreground/80 text-foreground/60"
            >
              Content Upserter
            </Link>
            <Link
              href="/vector-search"
              className="transition-colors hover:text-foreground/80 text-foreground/60"
            >
              Vector Search
            </Link>
          </nav>
          <div className="flex items-center space-x-4">
            <AuthButton />
            <ThemeToggle />
          </div>
        </div>
      </div>
    </header>
  );
}
