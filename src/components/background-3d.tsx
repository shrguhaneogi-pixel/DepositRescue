"use client";

import React, { useEffect, useRef, useState } from "react";
import { motion, useTransform, MotionValue } from "framer-motion";

interface Background3DProps {
  scrollYProgress: MotionValue<number>;
  mouseX: MotionValue<number>;
  mouseY: MotionValue<number>;
}

export default function Background3D({ scrollYProgress, mouseX, mouseY }: Background3DProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [splineLoaded, setSplineLoaded] = useState(false);
  const yParallax = useTransform(scrollYProgress, [0, 1], ["0%", "15%"]);
  const rotateParallax = useTransform(scrollYProgress, [0, 1], [0, 12]);

  useEffect(() => {
    // Dynamically load spline viewer script asynchronously to maintain GitHub repository under 10 MB
    const script = document.createElement("script");
    script.src = "https://unpkg.com/@splinetool/viewer@1.9.72/build/spline-viewer.js";
    script.type = "module";
    script.async = true;
    script.onload = () => setSplineLoaded(true);
    document.head.appendChild(script);

    return () => {
      if (document.head.contains(script)) {
        document.head.removeChild(script);
      }
    };
  }, []);

  // WebGL/Canvas Particle lattice renderer as real-time 3D ambient fallback & layer overlay
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId: number;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    let width = window.innerWidth;
    let height = window.innerHeight;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);

    const handleResize = () => {
      if (!canvas) return;
      const newDpr = Math.min(window.devicePixelRatio || 1, 2);
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width * newDpr;
      canvas.height = height * newDpr;
      ctx.scale(newDpr, newDpr);
    };
    window.addEventListener("resize", handleResize);

    // Particle nodes
    const particleCount = 45;
    const particles = Array.from({ length: particleCount }).map(() => ({
      x: Math.random() * width,
      y: Math.random() * height,
      z: Math.random() * 2 + 0.5,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      radius: Math.random() * 1.8 + 0.6,
    }));

    let targetMouseX = 0;
    let targetMouseY = 0;

    const unsubscribeMouseX = mouseX.on("change", (v: number) => { targetMouseX = v; });
    const unsubscribeMouseY = mouseY.on("change", (v: number) => { targetMouseY = v; });

    let angle = 0;

    const render = () => {
      angle += 0.003;
      ctx.clearRect(0, 0, width, height);

      // Deep radial background gradient
      const bgGrad = ctx.createRadialGradient(
        width / 2 + targetMouseX * 5,
        height / 2 + targetMouseY * 5,
        100,
        width / 2,
        height / 2,
        Math.max(width, height) * 0.8
      );
      bgGrad.addColorStop(0, "#121218");
      bgGrad.addColorStop(0.5, "#0a0a0e");
      bgGrad.addColorStop(1, "#050507");
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, width, height);

      // Draw subtle grid lines reacting to scroll/mouse
      ctx.strokeStyle = "rgba(255, 255, 255, 0.025)";
      ctx.lineWidth = 1;
      const gridSize = 80;
      const offsetX = (targetMouseX * 2) % gridSize;
      const offsetY = (targetMouseY * 2 + angle * 20) % gridSize;

      for (let x = offsetX; x < width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = offsetY; y < height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // Draw particle nodes & connecting lines
      for (let i = 0; i < particleCount; i++) {
        const p = particles[i];
        p.x += p.vx + (targetMouseX * 0.02) / p.z;
        p.y += p.vy + (targetMouseY * 0.02) / p.z;

        if (p.x < 0) p.x = width;
        if (p.x > width) p.x = 0;
        if (p.y < 0) p.y = height;
        if (p.y > height) p.y = 0;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius * p.z, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(244, 63, 94, ${0.18 * p.z})`;
        ctx.fill();

        // Connect nearby particles
        for (let j = i + 1; j < particleCount; j++) {
          const p2 = particles[j];
          const dx = p.x - p2.x;
          const dy = p.y - p2.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 140) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = `rgba(255, 255, 255, ${0.04 * (1 - dist / 140)})`;
            ctx.lineWidth = 0.8;
            ctx.stroke();
          }
        }
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener("resize", handleResize);
      unsubscribeMouseX();
      unsubscribeMouseY();
    };
  }, [mouseX, mouseY]);

  return (
    <motion.div
      style={{ y: yParallax, rotate: rotateParallax }}
      className="fixed inset-0 z-0 pointer-events-none overflow-hidden"
    >
      {/* Dynamic Spline 3D Scene Layer */}
      {splineLoaded && (
        <div className="absolute inset-0 opacity-40 mix-blend-screen transition-opacity duration-1000">
          <spline-viewer
            url="https://prod.spline.design/6Wnt1-GLOUvu5-OI/scene.splinecode"
            loading-anim-type="spinner"
            style={{ width: "100%", height: "100%" }}
          />
        </div>
      )}

      {/* 3D Canvas Background */}
      <canvas ref={canvasRef} className="absolute inset-0 w-full h-full" />

      {/* Editorial Vignette */}
      <div className="absolute inset-0 bg-radial from-transparent via-neutral-950/40 to-neutral-950/90 pointer-events-none" />
    </motion.div>
  );
}
