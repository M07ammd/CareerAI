---
title: CareerPilot AI
emoji: 🎯
colorFrom: gray
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: AI-powered career analysis — CV vs Job Description
---

# CareerPilot AI Backend

This Space hosts the FastAPI + LangGraph backend for CareerPilot AI.

**Frontend:** Deploy separately on Vercel pointing to this Space's URL.

## Required Secrets (set in Space Settings → Secrets)

| Secret | Description |
|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `TAVILY_API_KEY` | Optional — web search enrichment |
