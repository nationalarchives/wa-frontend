from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    scoped_session,
    sessionmaker,
)


class Base(DeclarativeBase):
    """Base class for all models with automatic id and timestamp tracking"""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


engine = None
db_session = None


def init_db(app):
    global engine, db_session

    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])

    session_factory = sessionmaker(bind=engine)
    db_session = scoped_session(session_factory)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return db_session
