# EDGEucator: Privacy-First AI Mentorship
**HackNYU 2024 Project** · Local AI Inference · 3D Visuals · Data Insights

EDGEucator is a privacy-focused educational platform that runs entirely on-device. By leveraging Qualcomm’s NPU to accelerate Llama 3B, it delivers a real-time AI mentor with **sub-2-second inference latency**, ensuring a child’s data never leaves local hardware.

---

## 🔗 Project Components

This project is split into two modules for cross-platform compatibility and clear, parent-friendly data visualization:

## 🔗 Repositories

- **EDGEucator 3D Avatar WebApp:** https://github.com/Srahin000/EDGEucatorWebApp  
- **EDGEucator Insights Dashboard:** https://github.com/Srahin000/EDGEucatorDashboard

### 1) EDGEucator 3D Avatar WebApp
**Problem:** Unity-based avatars often fail on Windows ARM architecture.  
**Solution:** A pure **Three.js + Ready Player Me** web stack with **Rhubarb viseme-based lip-sync**, enabling a lightweight, platform-agnostic 3D mentor interface.

### 2) EDGEucator Insights Dashboard
**Function:** A **Next.js 14** app that parses conversation data into:
- emotional trends  
- topic frequency  
- personalized after-school recommendations  

---

## 🛠️ The Technical Edge

The core innovation is local hardware acceleration for heavy AI workloads:

- **NPU Acceleration:** Uses Qualcomm’s NPU for local LLM execution  
- **Performance:** **< 2.0s inference** for conversational message generation using **Llama 3B**  
- **Privacy by Design:** No cloud APIs — transcription, LLM processing, and sentiment analysis happen locally  
- **Lip-Sync Engine:** Real-time jaw/mouth morph target animation driven by audio volume + **Rhubarb** viseme extraction  

---

## 🏗️ Architecture Overview

1. **Input:** Child speaks to the AI Mentor  
2. **Processing:** Qualcomm NPU runs the prompt through Llama 3B locally  
3. **Visualization:** Three.js WebApp renders the 3D response with synchronized lip-sync  
4. **Analytics:** Dashboard extracts insights from the local database to show parents emotional well-being trends and interests  

---

## 🚀 Getting Started

### Prerequisites
- **Node.js 18+**
- **Qualcomm AI Stack** (for hardware-accelerated features)

### Installation
Clone the repo and navigate to the module you want to run:

```bash
git clone https://github.com/Srahin000/hacknyu.git
cd hacknyu
