"""Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReviewOut(BaseModel):
    id: int
    contact_number: str
    user_name: str
    product_name: str
    product_review: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


