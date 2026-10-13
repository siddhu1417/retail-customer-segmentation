from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class Dataset(Base):
    __tablename__ = "datasets"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    path: Mapped[str] = mapped_column(Text)
    row_count: Mapped[int] = mapped_column(Integer)
    columns: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class Run(Base):
    __tablename__ = "runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"))
    k: Mapped[int] = mapped_column(Integer)
    features: Mapped[str] = mapped_column(Text)
    seed: Mapped[int] = mapped_column(Integer)
    inertia: Mapped[float] = mapped_column(Float)
    silhouette: Mapped[float | None] = mapped_column(Float, nullable=True)
    model_path: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class Result(Base):
    __tablename__ = "results"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"))
    customer_id: Mapped[str] = mapped_column(String(255))
    record: Mapped[str] = mapped_column(Text)
    cluster: Mapped[int] = mapped_column(Integer)
