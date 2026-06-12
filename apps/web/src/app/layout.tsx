import type { Metadata } from "next";
import { DM_Sans, Instrument_Serif, JetBrains_Mono, Press_Start_2P } from "next/font/google";
import "./globals.css";

const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
  weight: ["400", "500", "600", "700"],
});

const instrumentSerif = Instrument_Serif({
  subsets: ["latin"],
  variable: "--font-display",
  display: "swap",
  weight: ["400"],
  style: ["normal", "italic"],
});

const jetBrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
  weight: ["400", "500"],
});

const pressStart2P = Press_Start_2P({
  subsets: ["latin"],
  variable: "--font-pixel",
  display: "swap",
  weight: ["400"],
});

export const metadata: Metadata = {
  title: "VITALS — Game Health Monitor",
  description: "How broken is this game right now?",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${dmSans.variable} ${instrumentSerif.variable} ${jetBrainsMono.variable} ${pressStart2P.variable}`}>
      <body>
        <nav className="border-b border-border">
          <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
            <a href="/" className="font-pixel text-xs text-healthy tracking-tight">
              VITALS
            </a>
            <div className="flex gap-6 text-sm text-muted">
              <a href="/" className="hover:text-text transition-colors">
                Games
              </a>
              <a href="/admin" className="hover:text-text transition-colors">
                Admin
              </a>
            </div>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}
