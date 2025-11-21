"""FastAPI entrypoint."""

from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from twilio.request_validator import RequestValidator

from . import models, schemas, twilio_flow
from .config import get_settings
from .database import Base, engine, get_db

settings = get_settings()
app = FastAPI(title="WhatsApp Product Review Collector", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/reviews", response_model=List[schemas.ReviewOut])
def list_reviews(db: Session = Depends(get_db)) -> List[schemas.ReviewOut]:
    reviews = (
        db.query(models.Review)
        .order_by(models.Review.created_at.desc())
        .all()
    )
    return reviews


@app.post(
    "/webhook/whatsapp",
    response_class=PlainTextResponse,
    summary="Webhook that Twilio calls whenever a WhatsApp message is received.",
)
async def whatsapp_webhook(
    request: Request,
    db: Session = Depends(get_db),
) -> Response:
    form = await request.form()
    payload = {k: v for k, v in form.items()}

    signature = request.headers.get("X-Twilio-Signature", "")
    if settings.twilio_auth_token and settings.twilio_enable_validation:
        validator = RequestValidator(settings.twilio_auth_token)
        if not validator.validate(str(request.url), payload, signature):
            raise HTTPException(status_code=403, detail="Invalid Twilio signature.")

    contact_number = payload.get("From")
    body = payload.get("Body", "")

    if not contact_number:
        raise HTTPException(status_code=400, detail="Missing sender number.")

    result = twilio_flow.process_message(
        db, contact_number=contact_number, body=body
    )
    xml = twilio_flow.build_twiml_response(result.reply)
    return Response(content=xml, media_type="text/xml")


