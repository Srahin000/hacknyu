EDGEucator: Local AI-Powered Child Development & Mentorship
Winner/Project for HackNYU 2024 A privacy-first, NPU-accelerated platform for child-AI interaction and parental insights.

🚀 The Vision
Most AI educational tools rely on the cloud, compromising privacy and requiring high latency. EDGEucator runs entirely locally. By leveraging Qualcomm’s NPU, we achieve sub-2-second inference for Llama 3B, providing a seamless, real-time "AI Mentor" experience that is private by design.

🛠️ Tech Stack & Architecture
We split the project into two core modules to ensure cross-platform compatibility (specifically solving for Windows ARM) and a clean separation of concerns:

1. The AI Mentor Avatar (Frontend - WebApp)
A browser-based 3D experience designed to replace heavy Unity-based solutions that fail on ARM architecture.

Tech: Three.js, Ready Player Me, Web Audio API, TypeScript.

Key Feature: Professional viseme-based lip-sync using Rhubarb.

Innovation: Real-time mouth animation driven by local audio volume/morph targets.

2. Child Insights Dashboard (Frontend - Dashboard)
A Next.js 14 application that visualizes the "data behind the conversation."

Tech: Next.js (App Router), Tailwind CSS, Recharts, Lucide.

Key Feature: Emotional tone tracking, interest mapping, and personalized club/activity recommendations.

3. The "Brain" (Local Backend)
Model: Llama 3B.

Hardware Acceleration: Qualcomm NPU integration.

Performance: <2.0s inference time for conversational message generation.

Privacy: 100% local data processing; no data ever leaves the device.

📂 Repository Structure
This project is organized as a monorepo for the hackathon:

/EDGEucatorWebApp: The Three.js 3D Avatar interface.

/EDGEucatorDashboard: The Next.js analytics dashboard.

⚡ Quick Start
Prerequisites
Node.js 18+

Qualcomm AI Stack (for NPU acceleration features)

Installation
Clone the hub:

Bash
git clone https://github.com/Srahin000/hacknyu.git
cd hacknyu
Setup the Avatar:

Bash
cd EDGEucatorWebApp
npm install && npm run dev
Setup the Dashboard:

Bash
cd EDGEucatorDashboard
npm install && npm run dev
💡 Why This Matters
Windows ARM devices often struggle with native 3D engines like Unity. By building a Three.js + NPU pipeline, we proved that high-fidelity AI characters and deep data analytics can run efficiently on low-power, privacy-focused hardware.

This isn't just a chatbot; it's a private, local mentor that understands a child's growth.
