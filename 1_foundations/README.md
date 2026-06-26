---
title: career_conversation
emoji: 💬
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 5.49.1
app_file: app.py
pinned: false
---

# Week 1 — Foundations · Career Conversation Agent

The first project of my Agentic AI Engineering journey: an AI "career twin" that chats with
visitors about my background, answers questions from my résumé and a short bio, captures the
email of anyone who wants to get in touch, and pings my phone with a push notification — all
built **without any agentic framework**, then deployed to Hugging Face Spaces.

**Live demo:** https://huggingface.co/spaces/IzmaAnwar/career_conversation

---

## What's in this folder

| Path | What it is |
|------|------------|
| `1_lab1.ipynb` | First LLM calls · the messages format · local models via Ollama |
| `2_lab2.ipynb` | One OpenAI-compatible interface across many providers · LLM-as-a-judge |
| `3_lab3.ipynb` | The career chatbot · Gradio UI · evaluator + self-correction loop |
| `4_lab4.ipynb` | Tool use / function calling · Pushover notifications · deployment |
| `app.py` | The deployable app (what runs on Hugging Face Spaces) |
| `me/` | Your context: `summary.txt` (short bio) + a résumé PDF |
| `requirements.txt` | Dependencies for the Hugging Face Space |

---

## Prerequisites

- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/)** — the package/environment manager this repo uses
- A **[Groq API key](https://console.groq.com)** (free) — powers the chat in `app.py`
- *(Optional)* A **[Pushover](https://pushover.net/)** account (user key + app token) — for the
  "someone wants to connect" push notifications
- *(Optional, for the labs)* keys for OpenAI / Anthropic / Google / DeepSeek, and
  **[Ollama](https://ollama.com)** if you want to run models locally for free
- *(Optional)* A **[Hugging Face](https://huggingface.co)** account + write token to deploy

---

## Setup

**1. Clone the repo and enter it**
```bash
git clone <your-repo-url>
cd agents
```

**2. Install uv** (skip if you already have it)
```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**3. Install dependencies** (creates a `.venv` and fetches Python 3.12 if needed)
```bash
uv sync
```

**4. Create a `.env` file in the repo root** with your keys:
```dotenv
GROQ_API_KEY=your_groq_key_here

# Optional — only needed for the push notifications
PUSHOVER_USER=your_pushover_user_key
PUSHOVER_TOKEN=your_pushover_app_token
```

**5. Add your own profile to `me/`**
- Replace `me/summary.txt` with a few lines about you.
- Drop in your résumé/LinkedIn PDF, then point `app.py` at it
  (`reader = PdfReader("me/YourResume.pdf")`) and set `self.name = "Your Name"`.

---

## Run the app locally

```bash
cd 1_foundations
uv run python app.py
```

Gradio prints a local URL (e.g. `http://127.0.0.1:7860`) — open it in your browser and start
chatting. Press `Ctrl+C` in the terminal to stop.

> The app uses Groq's OpenAI-compatible endpoint with the `llama-3.3-70b-versatile` model
> (it supports tool calling). You can swap the model or provider in `app.py`.

---

## Run the labs (notebooks)

1. Open the repo in **VS Code / Cursor** with the **Python** and **Jupyter** extensions.
2. Open any notebook (`1_lab1.ipynb` → `4_lab4.ipynb`) and select the **`.venv`** kernel.
3. Run the cells top to bottom.

Labs 1–2 can use **Ollama** for free local models — install it, then:
```bash
ollama pull llama3.2
```

---

## Deploy to Hugging Face Spaces

The whole walkthrough is in `4_lab4.ipynb`. Short version:

```bash
uv tool install "huggingface_hub[cli]"
hf auth login --token YOUR_HF_TOKEN     # needs WRITE permission
cd 1_foundations
uv run gradio deploy                    # name it, pick cpu-basic, add your secrets
```

Set `GROQ_API_KEY`, `PUSHOVER_USER`, and `PUSHOVER_TOKEN` as **Space secrets** (Settings →
Variables and secrets) so the deployed app can read them.

---

## Concepts covered in Week 1

1. **LLM APIs & the messages format** — every chat is a list of `role`/`content` messages
2. **One interface, many models** — same OpenAI-style code for OpenAI, Claude, Gemini, DeepSeek, Groq, Ollama (just change the base URL)
3. **LLM-as-a-judge & self-correction** — one model evaluates another's answer and retries if it isn't good enough
4. **Tool use / function calling** — the model decides when to call your Python functions, looping until the task is done (this is what turns a chatbot into an *agent*)
5. **Build & ship** — wrap it in a Gradio UI and deploy to Hugging Face Spaces

---

*Built while following [The Complete Agentic AI Engineering Course](https://edwarddonner.com/2025/04/21/the-complete-agentic-ai-engineering-course/) by Ed Donner.*
