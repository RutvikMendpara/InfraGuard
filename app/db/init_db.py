from app.db.base import Base
from app.db.session import engine

from app.db.models import finding, scan_run  


def init_db():
    Base.metadata.create_all(bind=engine)