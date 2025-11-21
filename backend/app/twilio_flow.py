"""Conversation flow logic for WhatsApp reviews."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from .models import ConversationState, ConversationStep, Review


@dataclass
class ConversationResult:
    reply: str
    review: Optional[Review] = None


RESET_KEYWORDS = {"reset", "restart", "start"}


def _twiml(message: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f"<Response><Message>{message}</Message></Response>"
    )


def build_twiml_response(message: str) -> str:
    """Public helper to build TwiML message."""
    return _twiml(message)


def _get_or_create_state(db: Session, contact_number: str) -> ConversationState:
    state = (
        db.query(ConversationState)
        .filter(ConversationState.contact_number == contact_number)
        .one_or_none()
    )
    if state is None:
        state = ConversationState(
            contact_number=contact_number,
            step=ConversationStep.PRODUCT,
        )
        db.add(state)
        db.commit()
        db.refresh(state)
    return state


def process_message(db: Session, *, contact_number: str, body: str) -> ConversationResult:
    """Handle the finite state machine for a contact."""
    cleaned_body = (body or "").strip()

    if not cleaned_body:
        return ConversationResult(
            reply="Sorry, I didn't catch that. Please send the text again."
        )

    normalized = cleaned_body.lower()
    if normalized in RESET_KEYWORDS:
        db.query(ConversationState).filter(
            ConversationState.contact_number == contact_number
        ).delete()
        db.commit()
        # Recreate a clean state for this user
        _get_or_create_state(db, contact_number)
        return ConversationResult(
            reply="Conversation reset. Which product is this review for?"
        )

    state = _get_or_create_state(db, contact_number)

    if state.step == ConversationStep.PRODUCT:
        state.product_name = cleaned_body
        state.step = ConversationStep.USER
        db.commit()
        return ConversationResult(
            reply="Thanks! What's your name?",
        )

    if state.step == ConversationStep.USER:
        state.user_name = cleaned_body
        state.step = ConversationStep.REVIEW
        db.commit()
        return ConversationResult(
            reply=f"Hi {state.user_name.title()}! Please send your review for {state.product_name}.",
        )

    # Final step collects the review text
    review = Review(
        contact_number=contact_number,
        user_name=state.user_name or "Unknown",
        product_name=state.product_name or "Unknown",
        product_review=cleaned_body,
        created_at=datetime.utcnow(),
    )
    db.add(review)
    db.delete(state)
    db.commit()
    return ConversationResult(
        reply=(
            f"Thanks {review.user_name} — your review for {review.product_name} "
            "has been recorded."
        ),
        review=review,
    )


