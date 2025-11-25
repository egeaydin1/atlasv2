# Ege's Proactive AI Assistant

A highly advanced, proactive AI assistant system built with a microservices architecture.

## Architecture

The system is composed of the following microservices:

1.  **API Gateway**: Routes requests, handles Authentication (JWT).
2.  **Memory Service**: Interfaces with Qdrant (Vector DB) and PostgreSQL for RAG.
3.  **Scheduler Service**: Manages cron jobs (Daily summaries, Event checks).
4.  **Voice Service**: Handles Twilio Webhooks, Whisper STT, and TTS streaming.
5.  **Integration Hub**: Modular service managing Google/Jira/42 APIs.
6.  **Telegram Bot Service**: Handles user interaction via Telegram.

## Tech Stack

-   **Language**: Python 3.11+ (FastAPI)
-   **Databases**: PostgreSQL, Redis, Qdrant
-   **AI**: Claude 3.5 Sonnet, OpenAI Embeddings, Whisper, TTS
-   **Infrastructure**: Docker, Railway

## Getting Started

1.  **Environment Setup**:
    Copy `.env.example` to `.env` and fill in the required values.
    ```bash
    cp .env.example .env
    ```

2.  **Run with Docker Compose**:
    ```bash
    docker-compose up --build
    ```

## Directory Structure

-   `api_gateway/`: API Gateway service
-   `memory_service/`: Memory management (RAG)
-   `scheduler_service/`: Task scheduling
-   `voice_service/`: Voice call handling
-   `integration_hub/`: External API integrations
-   `telegram_bot/`: Telegram bot interface
-   `shared/`: Shared libraries and schemas
