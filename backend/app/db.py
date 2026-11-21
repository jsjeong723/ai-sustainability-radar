from datetime import datetime, timezone
from sqlalchemy import create_engine, String, Float, DateTime, UniqueConstraint, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from .config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

class Observation(Base):
    __tablename__ = "observations"
    __table_args__ = (UniqueConstraint("source", "series_id", "period", name="uq_source_series_period"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(20), index=True)
    indicator_code: Mapped[str] = mapped_column(String(50), index=True)
    series_id: Mapped[str] = mapped_column(String(100), index=True)
    metric_name: Mapped[str] = mapped_column(String(200))
    period: Mapped[str] = mapped_column(String(20), index=True)
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(100))
    geography: Mapped[str] = mapped_column(String(100), default="United States")
    source_url: Mapped[str] = mapped_column(Text)
    footnote: Mapped[str | None] = mapped_column(Text, nullable=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class CollectionRun(Base):
    __tablename__ = "collection_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(20), index=True)
    status: Mapped[str] = mapped_column(String(20))
    records_received: Mapped[int] = mapped_column(default=0)
    records_inserted: Mapped[int] = mapped_column(default=0)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

def init_db():
    Base.metadata.create_all(bind=engine)
