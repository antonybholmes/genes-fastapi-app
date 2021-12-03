from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

#SQLALCHEMY_DATABASE_URL = config('DATABASE_URL')
SQLALCHEMY_TRACKS_DATABASE_URL = "sqlite:///tracks.sqlite3"
#SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

TrackSession = sessionmaker(autocommit=False, autoflush=False, bind=create_engine(
    SQLALCHEMY_TRACKS_DATABASE_URL, connect_args={"check_same_thread": False}))

Base = declarative_base()

# Dependency


async def get_track_db():
    db = TrackSession()
    try:
        yield db
    finally:
        db.close()


def get_db(db_file: str):
    url = f'sqlite:///{db_file}'

    engine = create_engine(url, connect_args={"check_same_thread": False})
    db = Session(engine)
    
    return db
