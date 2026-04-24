from app.db.base import Base
from app.db.session import engine

# IMPORTANT: import models so SQLAlchemy registers them
from app.db.models import finding, scan_run  # noqa


def init_db():
    Base.metadata.create_all(bind=engine)