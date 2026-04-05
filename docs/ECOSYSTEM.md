# OpenManus MCP Ecosystem Positioning

This document clarifies the relationships and architectural boundaries between the various autonomous agent platforms in the current fleet.

## Core Hierarchy

| Platform | Role | Focus | Runtime |
| :--- | :--- | :--- | :--- |
| **Manus** | Commercial SaaS | Production Stability | Managed Cloud |
| **OpenManus** | FOSS Framework | Community Extension | Local/Bridge (managed) |
| **OpenClaw** | Local-First Runtime | Power User / Privacy | Local Python |
| **Robofang** | Physical Robotics | Hardware Orchestration | Unitree / Go2 / G1 |

---

## 1. Manus vs. OpenManus
- **Manus** is the foundational, close-sourced autonomous agent platform. It provides the "standard" for agentic behavior and tool-use in cloud environments.
- **OpenManus** (this project) is the Open-Source community implementation. It aims to replicate and extend Manus capabilities using open models (Llama 3, Qwen) and local tools. **OpenManus MCP** acts as the bridge, allowing Claude Desktop or other MCP-capable hosts to drive the OpenManus agent.

## 2. Relation to OpenClaw
- **OpenClaw** is a specialized runtime designed for maximum local control and privacy. While OpenManus focuses on "Manus-compatible" workflows, OpenClaw is built for industrial-grade local automation where data never leaves the workstation.
- Use **OpenManus MCP** when you want a managed bridge to the OpenManus agentic loop.
- Use **OpenClaw** when you need a dedicated, air-gapped autonomous engine for proprietary data processing.

## 3. Relation to Robofang
- **Robofang** is the physical substrate of our robotics fleet. It orchestrates real-world hardware (like the Unitree Go2 or G1 humanoid).
- OpenManus can be used *inside* a Robofang mission to provide "higher-level reasoning" (e.g., "Analyze this room and find the coffee machine"), while Robofang handles the low-level motor control and LiDAR navigation.

---

## Architectural Boundary
This MCP server (**openmanus-mcp**) is strictly a **control plane**. It does not bundle the OpenManus agent code. Instead, it:
1. Validates your local OpenManus installation.
2. Manages background agent jobs (via the Supervisor).
3. Proxies prompts and returns technical Markdown structured results (Mud-to-Gold).
