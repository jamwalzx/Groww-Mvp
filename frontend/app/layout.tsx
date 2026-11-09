import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Plan B for my SIP",
  description:
    "Educational tool for first-time SIP investors on Groww. Understand your options when a month feels tight — never investment advice.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">
        {/* Disclaimer banner — always visible on every screen */}
        <div className="disclaimer-banner bg-blue-50 border-b border-blue-200 px-4 py-2 text-center text-sm text-blue-700 font-medium">
          📚 Educational information only. Not investment advice.
        </div>
        <main className="max-w-3xl mx-auto px-4 py-8">{children}</main>
        <footer className="text-center text-xs text-gray-400 py-6 border-t border-gray-200 mt-12">
          <p>
            Plan B for my SIP — Educational tool for Groww users.{" "}
            <a
              href="https://groww.in/help"
              target="_blank"
              rel="noopener noreferrer"
              className="underline hover:text-gray-600"
            >
              Groww Help
            </a>
          </p>
          <p className="mt-1">
            🔒 Digits in your input are masked before analysis. Cards are saved on this device only.
          </p>
        </footer>
      </body>
    </html>
  );
}
