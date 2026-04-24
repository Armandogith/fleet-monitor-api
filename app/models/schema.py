from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from app.core.database import Base

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    drivers = relationship("Driver", back_populates="company")

class Driver(Base):
    __tablename__ = "drivers"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False) # Ex: 5511999999999
    company = relationship("Company", back_populates="drivers")
    documents = relationship("Document", back_populates="driver")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    doc_type = Column(String, nullable=False) # Ex: CNH, CRLV, Curso MOPP
    expiration_date = Column(Date, nullable=False)
    driver = relationship("Driver", back_populates="documents")
    notifications = relationship("NotificationLog", back_populates="document")

class NotificationLog(Base):
    __tablename__ = "notification_logs"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    status = Column(String, nullable=False) # success ou failed
    error_message = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    document = relationship("Document", back_populates="notifications")