from sqlalchemy import Column, Integer, String

from app.db.database import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    api_call_limit = Column(Integer, nullable=False)
    ai_token_limit = Column(Integer, nullable=False)
    price_cents = Column(Integer, nullable=False)   