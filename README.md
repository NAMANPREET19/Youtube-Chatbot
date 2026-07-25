<div align="center">

# 🎬 YouTube AI Chatbot

**Ask any YouTube video a question. Get an answer — with the exact timestamp it came from.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-RAG-1C3C3C?style=flat)](https://www.langchain.com/)
[![Groq](https://img.shields.io/badge/Groq-Llama%203.3%2070B-F55036?style=flat)](https://groq.com/)
[![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-4285F4?style=flat)](https://github.com/facebookresearch/faiss)
[![Chrome Extension](https://img.shields.io/badge/Chrome-Extension-4285F4?style=flat&logo=googlechrome&logoColor=white)](https://developer.chrome.com/docs/extensions/)

*A Chrome extension + FastAPI backend that turns any YouTube video's transcript into a searchable, chattable knowledge base using Retrieval-Augmented Generation.*

</div>

---
## 🎥 Demo

<!--
  Record a short screen capture: open a YouTube video → click the extension →
  type a question → answer appears with a [MM:SS] citation.
  10-15 seconds is plenty.

  1. Save your recording as a GIF, e.g. `demo.gif`, in a `/assets` folder in this repo.
  2. Replace the placeholder line below with:
       ![Demo](assets/demo.gif)
  3. (Optional) Also upload a longer walkthrough to YouTube/Loom and swap the
     link below.
-->

https://github.com/user-attachments/assets/c6661a0b-c52d-40d1-9999-c8058def666e


---


## What it does

Open a YouTube video, click the extension, and ask a question about it in plain English. The bot:

1. Pulls the video's transcript (with per-caption timestamps)
2. Chunks it intelligently and embeds it into a **FAISS** vector store
3. Retrieves the most relevant chunks using **MMR + multi-query retrieval**
4. Sends them to a **Groq-hosted Llama 3.3 70B** model to generate an answer
5. Returns the answer **with inline timestamp citations**, like:

   > "The speaker explains that gradient descent minimizes the loss function `[02:15]`."

No skimming through a 40-minute video to find the one part you needed.

---


## ✨ Features

- 🎯 **Timestamp-aware answers** — every claim in the response is cited back to `[MM:SS]` in the video
- 🔍 **Smarter retrieval** — MMR search + `MultiQueryRetriever` reformulates your question multiple ways to pull better context, not just a single nearest-neighbor lookup
- 🧠 **RAG pipeline** — grounded in the actual transcript, not the model's imagination
- 🧩 **Chrome Extension UI** — ask questions right from a popup while watching
- ⚡ **FastAPI backend** — a single `/chat` endpoint, easy to extend or swap the frontend
- 🌐 **Multi-language transcript support** — fetches `en`, `hi`, `en-US` captions
- 🚫 **Graceful handling** of disabled or age-restricted transcripts

---

## 🧠 How it works (architecture)

```
┌─────────────────────┐        ┌──────────────────────────────────────────┐
│  Chrome Extension    │  POST  │              FastAPI Backend              │
│  popup.html/js/css   │ ─────► │                  app.py                  │
│  (video_id + question)│        └──────────────────────┬───────────────────┘
└─────────────────────┘                                 │
                                                          ▼
                                          ┌───────────────────────────────┐
                                          │         transcript.py         │
                                          │  YouTubeTranscriptApi fetch   │
                                          │  → merge captions into text   │
                                          │  → RecursiveCharacterSplitter │
                                          │  → tag each chunk w/ timestamp│
                                          │  → embed (HF MiniLM) → FAISS  │
                                          └───────────────┬────────────────┘
                                                          ▼
                                          ┌───────────────────────────────┐
                                          │           chain.py            │
                                          │  MMR retriever (k=4, fetch_k=15)│
                                          │  → MultiQueryRetriever (Groq) │
                                          │  → format_docs (adds [MM:SS]) │
                                          │  → prompt → ChatGroq Llama 3.3│
                                          └───────────────┬────────────────┘
                                                          ▼
                                          Answer with inline [timestamp] citations
```

**Why this is more than a toy RAG demo:**
- Captions from YouTube are only a few words each — chunking them individually would destroy retrieval quality. `transcript.py` stitches captions into one continuous string first, *then* chunks it, while still tracking which timestamp each chunk originally came from.
- `MultiQueryRetriever` generates several rephrasings of the user's question via the LLM, then merges results — this catches relevant transcript sections that a single literal query would miss.
- The prompt explicitly requires the model to cite the timestamp for every claim it makes, which keeps answers grounded and verifiable against the source video.

---

## 🛠️ Tech Stack

| Layer | Tech |
|---|---|
| Backend API | FastAPI, Uvicorn |
| Orchestration | LangChain (`langchain-core`, `langchain-classic`, `langchain-community`) |
| LLM | Groq — `llama-3.3-70b-versatile` |
| Embeddings | Hugging Face Inference — `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| Vector store | FAISS |
| Transcripts | `youtube-transcript-api` |
| Frontend | Chrome Extension (Manifest V3) — vanilla HTML/CSS/JS |

---



## 📁 Project Structure

```
Youtube-Chatbot/
├── app.py               # FastAPI app — /chat endpoint
├── chain.py              # RAG chain: retriever + prompt + Groq LLM
├── transcript.py         # Transcript fetch, chunking, embeddings, FAISS store
├── manifest.json          # Chrome extension manifest (v3)
├── popup.html / .css / .js # Extension UI
├── requirements.txt
└── Untitled.ipynb         # Notebook / experimentation
```

---

## 🗺️ Future Improvements

- [ ] Multi-language answer generation (not just multi-language transcript ingestion)
- [ ] PDF / document support alongside YouTube videos
- [ ] Persist vector stores instead of rebuilding per request (currently re-embeds the transcript on every call)
- [ ] Polished, animated extension UI
- [ ] Deploy the backend (Render/Railway/Fly.io) so it's not localhost-only

---
## 🚀 How You Can Use My App

### 1. Clone the repo

```bash
git clone https://github.com/NAMANPREET19/Youtube-Chatbot.git
cd Youtube-Chatbot
```

### 2. Set up the backend

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Create a `.env` file in the project root with your API keys:

```env
groq_api_key=your_groq_api_key
huggingfacehub_api_token=your_huggingface_api_token
```

Get a free Groq key at [console.groq.com](https://console.groq.com) and a Hugging Face token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).

Run the API:

```bash
uvicorn app:app --reload
```

The server will be live at `http://127.0.0.1:8000`, exposing:

```
POST /chat
{
  "video_id": "dQw4w9WgXcQ",
  "question": "What is the main point of this video?"
}
```

### 3. Load the Chrome Extension

1. Open `chrome://extensions`
2. Enable **Developer mode** (top right)
3. Click **Load unpacked** and select this project's folder
4. Open any YouTube video, click the extension icon, and start asking questions

> The extension talks to `http://127.0.0.1:8000`, so the backend needs to be running locally for it to work.

---
