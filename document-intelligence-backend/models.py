from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    document_type = Column(String, nullable=False)
    structured_data = Column(Text, nullable=True)
    extracted_text = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    key_points = Column(Text, nullable=True)
    recommended_next_action = Column(Text, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())