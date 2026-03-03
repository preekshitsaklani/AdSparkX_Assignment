# 🏟️ Persona-Adaptive Customer Support Agent (PACSA)

> like a football team — different formations for different opponents

## What this does
- **Detects** customer persona (technical expert, frustrated user, business executive, general)
- **Retrieves** the right KB content from Pinecone
- **Adapts** response tone based on who's asking
- **Escalates** to human agent when needed (like substituting an injured player lol)

## Architecture — the formation
```
START → Intake → Persona Detection → [Route]
                                        ├─→ KB Retrieval → Response Gen → Quality Gate → [Route]
                                        │                                                  ├─→ Output (GOAL!)
                                        │                                                  ├─→ Retry (VAR check)
                                        │                                                  └─→ Escalation (red card)
                                        ├─→ Direct Response → Quality Gate
                                        └─→ Escalation (immediate red card)
```

built using **LangChain + LangGraph + NVIDIA NIM GLM-5 + Pinecone**
