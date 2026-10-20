from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.sql import func
from app.core.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    color = Column(String(20), nullable=True)
    content = Column(Text, nullable=False)
    source_format = Column(String(50), nullable=False)  # markdown, json, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_agents_category_name", "category", "name"),
    )


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, nullable=False, index=True)
    criteria_name = Column(String(255), nullable=False)
    criteria_description = Column(Text, nullable=True)
    score = Column(Integer, nullable=False)  # 0-100
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    action = Column(String(50), nullable=False)  # create, update, delete, import, export
    user_id = Column(String(255), nullable=True)
    changes = Column(Text, nullable=True)  # JSON diff
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_audit_entity", "entity_type", "entity_id"),
    )