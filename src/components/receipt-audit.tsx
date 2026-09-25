"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertCircle, CheckCircle2, ShieldAlert, Sparkles, Scale, FileText, ArrowRight, RefreshCw } from "lucide-react";

interface AuditedItem {
  item_name: string;
  original_cost: number;
  adjusted_cost: number;
  is_routine_maintenance: boolean;
  is_illegal: boolean;
  category: string;
  matched_flag?: string | null;
  explanation: string;
}

interface AuditResponse {
  raw_total: number;
  illegal_total: number;
  allowed_total: number;
  statutory_recovery: number;
  statutory_multiplier: number;
  items: AuditedItem[];
  summary: string;
}

const SAMPLE_NOTICE = `Itemized Move-Out Deductions:
1. Full interior wall repainting: $350.00
2. Routine carpet steam cleaning: $150.00
3. Small nail holes repair: $75.00
4. Broken bathroom window pane replacement: $220.00
5. Deep kitchen oven dusting & cleaning: $100.00`;

export default function ReceiptAudit() {
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [auditData, setAuditData] = useState<AuditResponse | null>(null);

  const handleAudit = async (textToAudit?: string) => {
    const text = textToAudit || inputText;
    if (!text.trim()) {
      setError("Please paste your landlord's itemized deduction notice.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Calls /api/py/audit which Next.js rewrites to /api/audit (handled by api/index.py)
      const res = await fetch("/api/py/audit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      if (!res.ok) {
        throw new Error(`Server returned status ${res.status}`);
      }

      const data: AuditResponse = await res.json();
      setAuditData(data);
    } catch (err: any) {
      console.error(err);
      setError("Failed to connect to audit serverless function.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
      {/* Left Input Section */}
      <div className="lg:col-span-6 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-emerald-500/10 text-emerald-400 rounded-lg">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Landlord Notice Input</h2>
            <p className="text-xs text-slate-400">Paste itemized charges or security deposit withholding text</p>
          </div>
        </div>

        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Paste landlord's itemized deduction text here (e.g. '$300 interior painting, $150 routine carpet cleaning...')"
          className="w-full h-56 p-4 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-mono text-sm leading-relaxed resize-none mb-4"
        />

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="flex flex-wrap items-center justify-between gap-3">
          <button
            type="button"
            onClick={() => {
              setInputText(SAMPLE_NOTICE);
              handleAudit(SAMPLE_NOTICE);
            }}
            className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1 font-medium transition-colors cursor-pointer"
          >
            <Sparkles className="w-3.5 h-3.5" />
            Load & Audit Sample Notice
          </button>

          <button
            type="button"
            disabled={loading}
            onClick={() => handleAudit()}
            className="px-6 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-sm transition-all flex items-center gap-2 shadow-lg shadow-emerald-500/20 disabled:opacity-50 cursor-pointer"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Auditing Deductions...
              </>
            ) : (
              <>
                Audit Statement
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>

      {/* Right Digital Receipt Audit Ledger */}
      <div className="lg:col-span-6">
        <AnimatePresence mode="wait">
          {auditData ? (
            <motion.div
              key="audit-result"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4 }}
              className="receipt-paper rounded-2xl p-6 sm:p-8 font-mono text-slate-900 border border-slate-300 relative overflow-hidden"
            >
              {/* Receipt Header */}
              <div className="text-center border-b-2 border-dashed border-slate-400 pb-5 mb-6">
                <div className="flex justify-center mb-1">
                  <div className="px-3 py-1 bg-slate-900 text-emerald-400 rounded text-xs font-bold uppercase tracking-wider">
                    DEPOSIT RESCUE AUDIT LEDGER
                  </div>
                </div>
                <h3 className="text-lg font-black tracking-tight uppercase text-slate-900 mt-2">STATUTORY DISPUTE RECEIPT</h3>
                <p className="text-[11px] text-slate-500">Vercel Serverless @vercel/python + Groq Pydantic v2</p>
              </div>

              {/* Line Items */}
              <div className="space-y-4 mb-6">
                <div className="flex justify-between text-xs font-bold text-slate-500 border-b border-slate-300 pb-1">
                  <span>CLAIMED DEDUCTION</span>
                  <span>ORIGINAL / AUDITED</span>
                </div>

                {auditData.items.map((item, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.15, duration: 0.3 }}
                    className="relative bg-white/60 p-3 rounded-lg border border-slate-200/80 shadow-xs"
                  >
                    <div className="flex justify-between items-start gap-2 mb-1">
                      <div className="relative font-bold text-sm text-slate-800 pr-2">
                        <span>{item.item_name}</span>
                        {item.is_illegal && (
                          <motion.div
                            initial={{ scaleX: 0 }}
                            animate={{ scaleX: 1 }}
                            transition={{ duration: 0.6, delay: 0.3 + idx * 0.15, ease: "easeInOut" }}
                            style={{ originX: 0 }}
                            className="absolute top-1/2 left-0 right-0 h-0.5 bg-rose-600 shadow-sm"
                          />
                        )}
                      </div>

                      <div className="text-right shrink-0">
                        {item.is_illegal ? (
                          <div className="flex flex-col items-end">
                            <span className="line-through text-xs text-rose-500 font-semibold">
                              ${item.original_cost.toFixed(2)}
                            </span>
                            <motion.span
                              initial={{ scale: 0.8 }}
                              animate={{ scale: [1, 1.15, 1] }}
                              transition={{ delay: 0.5 + idx * 0.15 }}
                              className="text-sm font-black text-emerald-600"
                            >
                              $0.00
                            </motion.span>
                          </div>
                        ) : (
                          <span className="text-sm font-bold text-slate-800">
                            ${item.original_cost.toFixed(2)}
                          </span>
                        )}
                      </div>
                    </div>

                    {item.is_illegal ? (
                      <div className="mt-2 text-xs bg-rose-50 border border-rose-200 text-rose-700 p-2 rounded flex items-start gap-1.5">
                        <ShieldAlert className="w-3.5 h-3.5 text-rose-600 shrink-0 mt-0.5" />
                        <div>
                          <span className="font-bold uppercase tracking-wider text-[10px] bg-rose-600 text-white px-1.5 py-0.5 rounded mr-1">
                            ILLEGAL WEAR & TEAR
                          </span>
                          <p className="mt-1 text-[11px] text-rose-800">{item.explanation}</p>
                        </div>
                      </div>
                    ) : (
                      <div className="mt-1 text-[11px] text-slate-500 flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3 text-slate-400" />
                        <span>{item.explanation}</span>
                      </div>
                    )}
                  </motion.div>
                ))}
              </div>

              {/* Financial Totals Breakdown */}
              <div className="border-t-2 border-dashed border-slate-400 pt-4 space-y-2 text-xs font-semibold text-slate-700">
                <div className="flex justify-between">
                  <span>Landlord Raw Claim Total:</span>
                  <span className="font-mono">${auditData.raw_total.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-rose-600 font-bold">
                  <span>Unlawful Wear & Tear Zeroed Out:</span>
                  <span className="font-mono">-${auditData.illegal_total.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-slate-900 border-t border-slate-300 pt-2 font-bold">
                  <span>Valid Allowed Tenant Deductions:</span>
                  <span className="font-mono">${auditData.allowed_total.toFixed(2)}</span>
                </div>
              </div>

              {/* Statutory Recovery Counter */}
              <motion.div
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.8, type: "spring", stiffness: 200 }}
                className="mt-6 p-4 rounded-xl bg-slate-900 text-white shadow-lg border border-emerald-500/40 relative overflow-hidden"
              >
                <div className="absolute top-0 right-0 p-3 opacity-10">
                  <Scale className="w-24 h-24 text-emerald-400" />
                </div>
                <div className="relative z-10">
                  <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold uppercase tracking-wider mb-1">
                    <Scale className="w-4 h-4" />
                    <span>STATUTORY RECOVERY ESTIMATE ({int(auditData.statutory_multiplier)}X PENALTY)</span>
                  </div>
                  <div className="flex items-baseline gap-2">
                    <motion.span
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 1.0, duration: 0.4 }}
                      className="text-3xl font-black tracking-tight text-emerald-400 font-mono"
                    >
                      ${auditData.statutory_recovery.toFixed(2)}
                    </motion.span>
                    <span className="text-xs text-slate-400">Recoverable in dispute</span>
                  </div>
                  <p className="mt-2 text-[11px] text-slate-300 leading-tight">
                    {auditData.summary}
                  </p>
                </div>
              </motion.div>
            </motion.div>
          ) : (
            <div className="h-full min-h-[420px] rounded-2xl border-2 border-dashed border-slate-800 bg-slate-900/50 p-8 flex flex-col items-center justify-center text-center text-slate-400">
              <Scale className="w-12 h-12 text-slate-600 mb-3 animate-pulse" />
              <h3 className="text-base font-semibold text-slate-300">No Audit Result Generated</h3>
              <p className="text-xs text-slate-500 max-w-xs mt-1">
                Paste your landlord notice on the left or click "Audit Sample Notice" to test live Framer Motion deduction strikethroughs & statutory recovery calculations.
              </p>
            </div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

function int(val: number): number {
  return Math.round(val);
}
