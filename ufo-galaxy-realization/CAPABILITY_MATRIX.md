# UFO Galaxy System Capability Matrix

## 1. Core Capabilities Overview

| Category | Key Capabilities | Primary Nodes |
|----------|------------------|---------------|
| **AI Brain** | Multi-Model Routing, Local Inference, Long-term Memory | `Node_01_OneAPI`, `Node_79_LocalLLM`, `Node_80_MemorySystem` |
| **Perception** | OCR, Multimodal Vision, Speech-to-Text, Real-time Audio | `Node_15_OCR`, `Node_90_MultimodalVision`, `Node_95_WebRTC` |
| **Control** | Android Automation, Windows UI Automation, 3D Printing | `Node_33_ADB`, `Node_45_DesktopAuto`, `Node_70_BambuLab` |
| **Knowledge** | Web Search, Academic Search, Knowledge Graph | `Node_25_GoogleSearch`, `Node_97_AcademicSearch`, `Node_103_KnowledgeGraph` |
| **Dev Tools** | Code Generation, Shell Execution, Git Operations | `Node_101_CodeEngine`, `Node_122_Shell`, `Node_07_Git` |
| **System** | Task Orchestration, Health Monitoring, Self-Healing | `Node_110_SmartOrchestrator`, `Node_67_HealthMonitor`, `Node_112_SelfHealing` |

## 2. Detailed Node Functions

### AI & Intelligence
*   **Node_01_OneAPI**: Central intelligence hub routing requests to GPT-4, Claude 3, Qwen, etc.
*   **Node_79_LocalLLM**: Runs local models (Llama 3, Mistral) for privacy-sensitive tasks.
*   **Node_80_MemorySystem**: Vector database (Qdrant) for storing and retrieving user context.
*   **Node_110_SmartOrchestrator**: Decomposes complex user goals into executable sub-tasks.

### Perception & Sensing
*   **Node_15_OCR**: High-precision text extraction from images/screenshots.
*   **Node_90_MultimodalVision**: Analyzes images and video frames to understand visual context.
*   **Node_17_EdgeTTS**: Converts text to natural-sounding speech (Microsoft Edge TTS).
*   **Node_95_WebRTC**: Handles real-time audio/video streaming from client devices.

### Device Control
*   **Node_33_ADB**: Low-level Android Debug Bridge wrapper for device management.
*   **Node_34_Scrcpy**: High-performance screen mirroring and control for Android.
*   **Node_45_DesktopAuto**: Windows desktop automation (mouse/keyboard simulation).
*   **Node_70_BambuLab**: IoT control for Bambu Lab 3D printers.

### Knowledge & Data
*   **Node_25_GoogleSearch**: Real-time web search for up-to-date information.
*   **Node_97_AcademicSearch**: ArXiv/Google Scholar integration for research papers.
*   **Node_83_NewsAggregator**: Fetches and summarizes news from RSS/API sources.
*   **Node_84_StockTracker**: Real-time financial data tracking.

## 3. System Workflow Examples

### Scenario A: "Research and Summarize"
1.  **User**: "Find the latest papers on Transformer efficiency."
2.  **Orchestrator**: Dispatches task to `Node_97_AcademicSearch`.
3.  **Search Node**: Retrieves top 5 papers from ArXiv.
4.  **OneAPI**: Summarizes abstracts into a coherent report.
5.  **Result**: Returns summary to user.

### Scenario B: "Cross-Device Copy Paste"
1.  **User**: "Copy the verification code from my phone."
2.  **Orchestrator**: Triggers `Node_33_ADB` to dump screen XML or `Node_15_OCR` to read screen.
3.  **Vision Node**: Extracts 6-digit code.
4.  **DesktopAuto**: Types the code into the active Windows window.

## 4. Deployment Status
*   **Codebase**: 108 Nodes (Complete)
*   **Dependencies**: `requirements.txt` (Complete)
*   **Configuration**: `node_dependencies.json` (Synced)
*   **Connectivity**: All ports and IDs resolved.

## 5. How to Start
1.  **Install Dependencies**: `pip install -r requirements.txt`
2.  **Start System**: `python unified_launcher.py`
3.  **Connect Client**: Launch Android App and connect to server IP.
