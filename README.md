# Basic Chat Web App

A simple, modern web chat interface for interacting with a self-hosted LLM, built with FastAPI and vanilla JavaScript.

---

## Purpose

This app provides a clean, responsive web interface for chatting with a self-hosted LLM. It supports:
- Real-time streaming responses
- Markdown rendering for bot messages
- Modern UI with message bubbles

---

## Features

- **Real-time Chat**: WebSocket-based streaming for instant interaction
- **Markdown Support**: Bot responses are rendered as formatted HTML
- **Responsive UI**: Works on desktop and mobile
- **Lightweight**: No frontend framework, just HTML/CSS/JS

---

## Installation

### Prerequisites

- [UV](https://github.com/astral-sh/uv) (for dependency management)
- A running model instance at `http://localhost:1234` (LM Studio works)

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mistral-chat-web.git
   cd mistral-chat-web
   ```

2. Copy the `.env-example` to a `.env` file and adjust accordingly to match your local model deployment.

3. Install the dependencies with `uv sync --all-groups`

4. Run with `uv run app.py`