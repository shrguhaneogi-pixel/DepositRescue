"use client";

import React, { useEffect } from "react";
import { motion, useScroll, useTransform, useMotionValue, useSpring } from "framer-motion";
import ReceiptAudit from "@/components/receipt-audit";
import Background3D from "@/components/background-3d";
import { ShieldCheck, Scale, Zap } from "lucide-react";

export default function Home() {
  const { scrollYProgress } = useScroll();

  // Mouse parallax motion values
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  const springConfig = { damping: 25, stiffness: 120 };
  const smoothMouseX = useSpring(mouseX, springConfig);
  const smoothMouseY = useSpring(mouseY, springConfig);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const { clientX, clientY } = e;
      const { innerWidth, innerHeight } = window;
      mouseX.set((clientX / innerWidth - 0.5) * 50);
      mouseY.set((clientY / innerHeight - 0.5) * 50);
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, [mouseX, mouseY]);

  // Layer Parallax Transforms
  // Layer 3 (Foreground typography / Hero): Fast parallax
  const yLayer3 = useTransform(scrollYProgress, [0, 1], ["0%", "-20%"]);
  // Layer 2 (Midground Interaction Area): Medium parallax
  const yLayer2 = useTransform(scrollYProgress, [0, 1], ["0%", "-8%"]);

  return (
    <main className="relative min-h-screen bg-neutral-950 text-neutral-100 overflow-hidden font-sans">
      {/* Layer 1: Deep Background (Slow Parallax + Reacts to Scroll & Mouse) */}
      <Background3D
        scrollYProgress={scrollYProgress}
        mouseX={smoothMouseX}
        mouseY={smoothMouseY}
      />

      {/* Main Multi-Plane Content Container */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 sm:pt-24 pb-24">
        
        {/* Layer 3: Foreground Headline Overlay */}
        <motion.div style={{ y: yLayer3 }} className="text-center mb-16 sm:mb-20">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/5 border border-white/10 text-neutral-300 text-[10px] font-mono uppercase tracking-widest mb-8 backdrop-blur-md"
          >
            <Zap className="w-3 h-3 text-rose-500" />
            <span>DEPOSITRESCUE // AUTOMATED DISPUTE ENGINE</span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.1 }}
            className="text-5xl sm:text-7xl lg:text-9xl font-serif font-bold tracking-tight text-white leading-[0.95] mb-6 drop-shadow-2xl"
          >
            Reclaim Your Deposit.
          </motion.h1>

          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-2xl sm:text-4xl lg:text-5xl font-serif italic font-light text-neutral-400 tracking-tight mb-10"
          >
            Justice, Automated.
          </motion.h2>

          {/* Minimalist Tech Badges */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="flex flex-wrap items-center justify-center gap-6 text-[10px] font-mono tracking-widest text-neutral-500 uppercase"
          >
            <div className="flex items-center gap-2 px-3 py-1 rounded-md bg-neutral-900/80 border border-white/5 backdrop-blur-md">
              <ShieldCheck className="w-3.5 h-3.5 text-rose-500" />
              <span>ROUTINE WEAR & TEAR SLASHER</span>
            </div>
            <div className="flex items-center gap-2 px-3 py-1 rounded-md bg-neutral-900/80 border border-white/5 backdrop-blur-md">
              <Scale className="w-3.5 h-3.5 text-emerald-400" />
              <span>STATUTORY MULTIPLIER MATH</span>
            </div>
          </motion.div>
        </motion.div>

        {/* Layer 2: Midground Floating Interaction Area */}
        <motion.div style={{ y: yLayer2 }}>
          <ReceiptAudit />
        </motion.div>

        {/* Minimalist Editorial Footer */}
        <footer className="mt-28 pt-8 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-4 text-[10px] font-mono tracking-widest text-neutral-600 uppercase">
          <div>DEPOSITRESCUE &bull; SMALL CLAIMS DISPUTE SYSTEM</div>
          <div>ZERO-CONFIG SERVERLESS ENGINE</div>
        </footer>
      </div>
    </main>
  );
}
