# WhatsApp Product Review Collector

Full-stack assignment implementation that collects WhatsApp product reviews through Twilio, persists them in Postgres, and displays them via a React dashboard.

## Architecture

- **WhatsApp** → Twilio sandbox forwards inbound messages to `/webhook/whatsapp`.
- **FastAPI backend** orchestrates the conversation flow, validates optional Twilio signatures, and stores final reviews in Postgres.
- **React (Vite) frontend** polls `GET /api/reviews` and renders a responsive table.
- **Postgres** stores `reviews` and in-flight `conversation_states`.

```
WhatsApp ➜ Twilio Sandbox ➜ FastAPI webhook ➜ Postgres
                                          ↘︎ React dashboard
```

## Prerequisites

- Python 3.11+
- Node 18+ and npm
- Postgres 14+ (or run via Docker)
- Twilio account with WhatsApp sandbox access

## Backend Setup

```bash
cd backend
python -m venv .venv && .venv\Scripts\activate  # or source .venv/bin/activate
pip install -r requirements.txt
copy env.sample .env  # update DATABASE_URL + Twilio token
uvicorn app.main:app --reload
```

- Tables are auto-created on startup.
- Docs live at `http://localhost:8000/docs`.

### Running with Docker Compose

```bash
docker compose up --build
```

This launches Postgres (port 5432) and the FastAPI service (port 8000).

## Twilio WhatsApp Sandbox

1. Join the sandbox in the Twilio console and note the sandbox number + join code.
2. Expose your local backend: `ngrok http 8000`.
3. Configure the sandbox **When a message comes in** URL to `https://<ngrok-domain>/webhook/whatsapp`.
4. Optional security: set `TWILIO_AUTH_TOKEN` in the backend `.env` to enable signature validation.

The conversation flow automatically collects product name → user name → review. Users can send `reset` anytime to restart.

## Frontend Setup

```bash
cd frontend
cp env.sample .env            # adjust VITE_API_BASE_URL if needed
npm install
npm run dev                   # opens http://localhost:5173
```

`npm run build` outputs a production bundle under `frontend/dist`.

## API Contract

- `POST /webhook/whatsapp` – Twilio webhook (returns TwiML).
- `GET /api/reviews` – Returns an array of reviews ordered by newest first.
- `GET /health` – Liveness probe.

Example response:

```json
[
  {
    "id": 3,
    "contact_number": "+1415XXXXXXX",
    "user_name": "Aditi",
    "product_name": "iPhone 15",
    "product_review": "Amazing battery life!",
    "created_at": "2025-11-21T08:24:12.345Z"
  }
]
```

## Testing & Demo Suggestions

- Use `ngrok` + your phone’s WhatsApp to record a quick screencast showing:
  1. Conversation with the bot.
  2. Review appearing on `http://localhost:5173`.
- Automated tests are limited for brevity; recommended next steps:
  - Add FastAPI unit tests around `twilio_flow.process_message`.
  - Add React component tests with Vitest/RTL.

## Folder Structure

```
backend/
  app/
frontend/
docker-compose.yml
README.md
SDE Assignment (1).pdf
```

## Troubleshooting

- **Signature errors**: ensure ngrok URL matches Twilio webhook config and `.env` token equals the account’s auth token.
- **Database connection**: confirm `DATABASE_URL` is reachable; default expects Postgres on localhost:5432 with database `reviews`.
- **CORS**: backend allows all origins for rapid testing; tighten in production via `allowed_origins` in `app/config.py`.

Happy building!


