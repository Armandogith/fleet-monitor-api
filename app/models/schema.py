from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    responsible_email = Column(String, nullable=True)
    responsible_whatsapp = Column(String, nullable=True)
    plan_type = Column(String, nullable=False, default="demo")   # "demo" | "full"
    plan_expires_at = Column(Date, nullable=True)
    access_key = Column(String, nullable=True, unique=True)      # DEMO-XXXX / FULL-XXXX

    drivers = relationship("Driver", back_populates="company", cascade="all, delete")


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    company = relationship("Company", back_populates="drivers")
    documents = relationship("Document", back_populates="driver", cascade="all, delete")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    doc_type = Column(String, nullable=False)
    expiration_date = Column(Date, nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False)

    driver = relationship("Driver", back_populates="documents")
    logs = relationship("NotificationLog", back_populates="document", cascade="all, delete")


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    status = Column(String, nullable=False)
    error_message = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="logs")