import React from "react";
import ReceiptAudit from "@/components/receipt-audit";
import { ShieldCheck, Scale, Cpu, Sparkles } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 py-12 px-4 sm:px-6 lg:px-8 selection:bg-emerald-500 selection:text-slate-950">
      {/* Hero Header */}
      <div className="max-w-6xl mx-auto text-center mb-12">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-4 shadow-sm">
          <Sparkles className="w-3.5 h-3.5" />
          DepositRescue MVP &bull; Hackathon Edition
        </div>
        <h1 className="text-4xl sm:text-5xl font-black tracking-tight text-white mb-4">
          Slash Illegal Landlord Charges. <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400">
            Recover Your Security Deposit.
          </span>
        </h1>
        <p className="max-w-2xl mx-auto text-slate-400 text-base sm:text-lg">
          Powered by FastAPI & Groq Pydantic v2 structured extraction. Automatically detects routine wear & tear, zeroes out unlawful deductions, and computes statutory 2x dispute recovery amounts.
        </p>

        {/* Technical Badges */}
        <div className="flex flex-wrap items-center justify-center gap-4 mt-6 text-xs text-slate-400 font-medium">
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-md bg-slate-900 border border-slate-800">
            <Cpu className="w-3.5 h-3.5 text-emerald-400" />
            FastAPI + Pydantic v2
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-md bg-slate-900 border border-slate-800">
            <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
            Groq LLM Open Model
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-md bg-slate-900 border border-slate-800">
            <Scale className="w-3.5 h-3.5 text-amber-400" />
            Deterministic Math Engine
          </div>
        </div>
      </div>

      {/* Main Interactive Receipt Component */}
      <ReceiptAudit />

      {/* Footer */}
      <footer className="max-w-6xl mx-auto mt-16 pt-8 border-t border-slate-800 text-center text-xs text-slate-500">
        <p>DepositRescue &bull; Security Deposit Dispute & Small Claims Audit Packager</p>
        <p className="mt-1">Antigravity Pythonic Architecture &bull; Monorepo Size Optimized (&lt;10 MB)</p>
      </footer>
    </main>
  );
}
