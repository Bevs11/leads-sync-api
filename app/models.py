from sqlalchemy import Column, Integer,  DateTime, JSON
from datetime import datetime
from app.database import Base

class ImportLog(Base):
    __tablename__ = "import_logs"

    id = Column(Integer, primary_key=True, index=True)
    total_rows = Column(Integer, nullable=False)
    created_count = Column(Integer, nullable=False)
    updated_count = Column(Integer, nullable=False)
    error_count = Column(Integer, nullable=False)
    details = Column(JSON, nullable=True) 
    errors = Column(JSON, nullable=True)  
    created_at = Column(DateTime, default=datetime.utcnow)
