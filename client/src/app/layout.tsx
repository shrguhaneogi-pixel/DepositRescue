import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DepositRescue - Security Deposit Dispute & Small Claims Packager",
  description: "Audit landlord itemized deductions, slash illegal routine maintenance charges, and calculate statutory deposit recovery.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased bg-slate-950 text-slate-100">
        {children}
      </body>
    </html>
  );
}
