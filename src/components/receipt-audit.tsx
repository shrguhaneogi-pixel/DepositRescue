"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, RefreshCw, AlertCircle, ShieldAlert, Check, Sparkles, Scale, Terminal } from "lucide-react";

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
    const text = textToAudit !== undefined ? textToAudit : inputText;
    if (!text.trim()) {
      setError("Paste itemized landlord deduction text to run statutory audit.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Primary API endpoint: /api/py/audit (maps to /api/audit on Vercel, proxied to port 8000 in dev)
      let res = await fetch("/api/py/audit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      if (res.status === 404) {
        res = await fetch("/api/audit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text }),
        });
      }

      if (!res.ok) {
        const errJson = await res.json().catch(() => null);
        const serverDetail = errJson?.detail;
        if (typeof serverDetail === "string") {
          throw new Error(serverDetail);
        } else if (Array.isArray(serverDetail) && serverDetail.length > 0) {
          throw new Error(serverDetail[0]?.msg || "Validation error");
        }
        throw new Error(`Server returned HTTP ${res.status}`);
      }

      const data: AuditResponse = await res.json();
      setAuditData(data);
    } catch (err: unknown) {
      console.error(err);
      if (err instanceof Error && err.message) {
        setError(err.message);
      } else {
        setError("Audit server error. Please check serverless function connection.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
      {/* Layer 2: Midground Input Interaction Plane (Glassmorphic Card) */}
      <div className="lg:col-span-6 glass-plane glass-plane-hover rounded-3xl p-6 sm:p-8 backdrop-blur-2xl relative z-20">
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-pulse" />
            <span className="text-xs font-mono tracking-widest uppercase text-neutral-400">
              01 // INPUT DISPUTE NOTICE
            </span>
          </div>
          <span className="text-[10px] font-mono tracking-wider text-neutral-400 uppercase px-2 py-0.5 rounded bg-neutral-900 border border-white/5">
            GROQ PYDANTIC V2
          </span>
        </div>

        <div className="relative mb-6">
          <label htmlFor="dispute-notice-input" className="sr-only">
            Landlord Itemized Deduction Notice Text
          </label>
          <textarea
            id="dispute-notice-input"
            value={inputText}
            aria-label="Landlord Itemized Deduction Notice Text"
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Paste landlord's itemized deduction notice here..."
            className="w-full h-64 p-5 rounded-2xl bg-neutral-950/80 border border-white/10 text-neutral-100 placeholder:text-neutral-400 focus:outline-none focus:border-rose-500/50 focus:ring-1 focus:ring-rose-500/50 font-mono text-xs leading-relaxed resize-none transition-all selection:bg-rose-500/30"
          />
          <div className="absolute bottom-4 right-4 text-[10px] font-mono text-neutral-400 pointer-events-none">
            {inputText.length} CHARS
          </div>
        </div>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            role="alert"
            aria-live="polite"
            className="mb-6 p-4 rounded-xl bg-rose-950/40 border border-rose-500/30 text-rose-300 text-xs font-mono flex items-center gap-3"
          >
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{error}</span>
          </motion.div>
        )}

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
          <button
            type="button"
            onClick={() => {
              setInputText(SAMPLE_NOTICE);
              handleAudit(SAMPLE_NOTICE);
            }}
            className="text-xs font-mono tracking-wider text-neutral-400 hover:text-white flex items-center justify-center sm:justify-start gap-2 py-2 transition-colors cursor-pointer group"
          >
            <Sparkles className="w-3.5 h-3.5 text-rose-400 group-hover:rotate-12 transition-transform" />
            <span>LOAD SAMPLE NOTICE</span>
          </button>

          <button
            type="button"
            disabled={loading}
            aria-busy={loading}
            onClick={() => handleAudit()}
            className="px-8 py-3.5 rounded-xl bg-white text-neutral-950 font-semibold text-xs tracking-widest uppercase hover:bg-neutral-200 active:scale-98 transition-all flex items-center justify-center gap-3 shadow-xl shadow-white/5 disabled:opacity-50 cursor-pointer"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin text-neutral-950" />
                <span>AUDITING...</span>
              </>
            ) : (
              <>
                <span>AUDIT STATEMENT</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>

      {/* Layer 3: Foreground Dispute Ledger & Statutory Penalty Counter */}
      <div className="lg:col-span-6 relative z-30" aria-live="polite">
        <AnimatePresence mode="wait">
          {auditData ? (
            <motion.div
              key="audit-result"
              initial={{ opacity: 0, y: 30, scale: 0.97 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -20, scale: 0.97 }}
              transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
              className="editorial-ledger rounded-3xl p-6 sm:p-8 border border-white/10 relative overflow-hidden backdrop-blur-xl"
            >
              {/* Header */}
              <div className="flex items-center justify-between border-b border-white/10 pb-5 mb-6">
                <div>
                  <span className="text-[10px] font-mono tracking-widest text-neutral-500 uppercase block mb-1">
                    02 // DISPUTE LEDGER
                  </span>
                  <h3 className="text-xl font-serif font-bold text-white tracking-tight">
                    Statutory Dispute Audit
                  </h3>
                </div>
                <div className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[10px] font-mono font-bold tracking-widest uppercase flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                  AUDITED
                </div>
              </div>

              {/* Items List */}
              <div className="space-y-3 mb-6" role="list">
                {auditData.items.map((item, idx) => (
                  <motion.div
                    key={idx}
                    role="listitem"
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.1, duration: 0.4 }}
                    className={`p-4 rounded-xl border transition-all ${
                      item.is_illegal
                        ? "bg-rose-950/20 border-rose-500/20"
                        : "bg-neutral-900/60 border-white/5"
                    }`}
                  >
                    <div className="flex justify-between items-start gap-4 mb-2">
                      <div className="flex-1">
                        <span className="relative inline-block font-mono text-xs font-semibold text-neutral-200">
                          {item.item_name}

                          {/* Red Slash Strikethrough Animation for Unlawful Deductions */}
                          {item.is_illegal && (
                            <motion.div
                              initial={{ scaleX: 0 }}
                              animate={{ scaleX: 1 }}
                              transition={{ duration: 0.5, delay: 0.3 + idx * 0.1, ease: "easeInOut" }}
                              style={{ originX: 0 }}
                              className="absolute top-1/2 left-0 right-0 h-[2.5px] strike-red rounded-full"
                            />
                          )}
                        </span>
                      </div>

                      <div className="text-right shrink-0 font-mono text-xs">
                        {item.is_illegal ? (
                          <div className="flex items-center gap-2">
                            <span className="sr-only">Original cost: </span>
                            <span className="line-through text-rose-300 font-medium">
                              ${item.original_cost.toFixed(2)}
                            </span>
                            <span className="sr-only">Reduced to: </span>
                            <motion.span
                              initial={{ scale: 0.8, opacity: 0 }}
                              animate={{ scale: [1, 1.2, 1], opacity: 1 }}
                              transition={{ delay: 0.5 + idx * 0.1, duration: 0.3 }}
                              className="text-emerald-400 font-bold tracking-wider"
                            >
                              $0.00
                            </motion.span>
                          </div>
                        ) : (
                          <span className="text-neutral-300 font-medium">
                            ${item.original_cost.toFixed(2)}
                          </span>
                        )}
                      </div>
                    </div>

                    {item.is_illegal ? (
                      <div className="mt-2 text-[11px] font-mono text-rose-300/90 bg-rose-950/40 p-2.5 rounded-lg border border-rose-500/20 flex items-start gap-2 leading-relaxed">
                        <ShieldAlert className="w-3.5 h-3.5 text-rose-400 shrink-0 mt-0.5" />
                        <div>
                          <span className="font-bold text-[9px] tracking-widest uppercase bg-rose-500 text-neutral-950 px-1.5 py-0.5 rounded mr-1.5">
                            ILLEGAL DEDUCTION
                          </span>
                          <span>{item.explanation}</span>
                        </div>
                      </div>
                    ) : (
                      <div className="mt-1.5 text-[11px] font-mono text-neutral-400 flex items-center gap-2">
                        <Check className="w-3 h-3 text-neutral-500" />
                        <span>{item.explanation}</span>
                      </div>
                    )}
                  </motion.div>
                ))}
              </div>

              {/* Financial Totals Breakdown */}
              <div className="border-t border-white/10 pt-4 space-y-2 text-xs font-mono text-neutral-400 mb-6">
                <div className="flex justify-between">
                  <span>Landlord Original Claimed Total:</span>
                  <span className="text-neutral-200">${auditData.raw_total.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-rose-400 font-semibold">
                  <span>Illegal Deductions Zeroed Out:</span>
                  <span>-${auditData.illegal_total.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-neutral-200 border-t border-white/10 pt-2 font-bold">
                  <span>Allowed Tenant Deductions:</span>
                  <span>${auditData.allowed_total.toFixed(2)}</span>
                </div>
              </div>

              {/* Statutory Recovery Counter */}
              <motion.div
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.6, duration: 0.4 }}
                className="p-5 rounded-2xl bg-gradient-to-br from-neutral-900 via-neutral-950 to-neutral-900 border border-emerald-500/40 relative overflow-hidden shadow-2xl"
              >
                <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none">
                  <Scale className="w-32 h-32 text-emerald-400" />
                </div>
                <div className="relative z-10">
                  <div className="flex items-center gap-2 text-emerald-400 text-[10px] font-mono font-bold tracking-widest uppercase mb-1">
                    <Scale className="w-3.5 h-3.5" />
                    <span>STATUTORY RECOVERY ESTIMATE ({Math.round(auditData.statutory_multiplier ?? 2)}X PENALTY)</span>
                  </div>
                  <div className="flex items-baseline gap-3 my-1">
                    <motion.span
                      initial={{ y: 10, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      transition={{ delay: 0.8, duration: 0.4 }}
                      className="text-4xl font-black font-mono tracking-tight text-emerald-400"
                    >
                      ${auditData.statutory_recovery.toFixed(2)}
                    </motion.span>
                    <span className="text-xs font-mono text-neutral-400 uppercase tracking-wider">
                      RECOVERABLE IN SMALL CLAIMS
                    </span>
                  </div>
                  <p className="mt-2 text-xs text-neutral-300 font-sans leading-relaxed border-t border-emerald-500/20 pt-2">
                    {auditData.summary}
                  </p>
                </div>
              </motion.div>
            </motion.div>
          ) : (
            <div className="h-full min-h-[460px] rounded-3xl border border-dashed border-white/10 bg-neutral-950/40 p-8 flex flex-col items-center justify-center text-center backdrop-blur-xl">
              <div className="w-12 h-12 rounded-2xl bg-neutral-900 border border-white/10 flex items-center justify-center text-neutral-500 mb-4">
                <Terminal className="w-6 h-6" />
              </div>
              <h4 className="text-sm font-mono tracking-widest text-neutral-300 uppercase mb-2">
                AWAITING INPUT
              </h4>
              <p className="text-xs font-mono text-neutral-500 max-w-xs leading-relaxed">
                Paste itemized notice or click "LOAD SAMPLE NOTICE" to activate automated strikethroughs & statutory recovery calculations.
              </p>
            </div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
