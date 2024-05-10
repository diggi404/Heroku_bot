from sqlalchemy import (
    DECIMAL,
    Column,
    Integer,
    BIGINT,
    String,
    Boolean,
    TIMESTAMP,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class HerokuTokens(Base):
    __tablename__ = "heroku_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, nullable=False)
    token = Column(String, nullable=False)
    email = Column(String, nullable=True)
    name = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, onupdate=datetime.utcnow)
