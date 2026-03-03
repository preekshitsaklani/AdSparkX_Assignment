# 🏟️ AdSparkX Assignment: Persona-Adaptive Customer Support Agent (PACSA)

## What is this?
Hey there! 👋 This is my submission for the AdSparkX assignment. I built a **Persona-Adaptive Customer Support Agent (PACSA)** using LangGraph, LangChain, NVIDIA NIM (GLM-5), and Pinecone.

Instead of a boring, generic chatbot, this one actually detects *who* it's talking to and changes its tactic—kind of like a football manager changing formations mid-game based on the opponent.

### 🎭 The Personas:
1. **Technical Expert**: Gets straight to the point, uses code snippets, no "fluff" or fake empathy.
2. **Frustrated User**: Gets immediate empathy, simple steps, and a quick escalation path.
3. **Business Executive**: Gets ROI metrics, SLAs, and bullet points (because execs don't read paragraphs).
4. **General User**: Gets warm, patient, step-by-step guidance.

### 🧠 The Architecture
It uses a stateful 8-node LangGraph workflow:
`Intake -> Persona Detection -> KB Retrieval (Pinecone) -> Response Gen -> Quality Gate (VAR Check) -> Output or Escalation`

There's even a **Quality Gate** that acts like a referee. If a response isn't grounded (hallucination) or the tone doesn't match the persona, it rejects it and tries again!

---

## 🛠️ How to run it

Everything is packed into a single, easy-to-use Jupyter Notebook (`PACSA_Agent.ipynb`). 

### Prerequisites
You'll need a `.env` file in the same directory with these keys:
```env
NVIDIA_API_KEY="your-nvapi-key"
NVIDIA_MODEL="z-ai/glm5"

PINECONE_API_KEY="your-pinecone-key"
PINECONE_INDEX="adsparkx-assignment"
PINECONE_HOST="your-pinecone-host-url"
PINECONE_EMBED_MODEL="llama-text-embed-v2"
```

### Setup Steps
1. Clone the repo
2. Open `PACSA_Agent.ipynb` in your favorite IDE (Jupyter, VS Code, Google Colab).
3. Run the very first cell to install requirements (`!pip install -r requirements.txt`).
4. Run all the cells one by one!

---

## ⚠️ IMPORTANT NOTE ON EXECUTION TIME

The LLM doing the heavy lifting here is NVIDIA's **GLM-5**, which is a *reasoning* model. It literally "thinks" internally before returning a response to ensure high quality and accurate persona alignment. 

Because of this deep thinking and the multi-node graph structure (which includes KB retrieval, response generation, and a separate LLM call for the Quality Gate referee), **the final test cell (Cell #11) takes around 6 minutes and 48.6 seconds to process completely.** 

Grab a coffee ☕ while it runs the 5 test scenarios—it's worth the wait!

---

*Built with ❤️ and way too much football terminology.*
