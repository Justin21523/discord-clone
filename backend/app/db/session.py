# backend/app/db/session.py
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import QueuePool
from backend.app.core.config import settings

# Configure database engine with connection pooling
# check_same_thread=False is required for SQLite in multithreaded environments like FastAPI
connect_args = {"check_same_thread": False}

# Create engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    poolclass=QueuePool,
    pool_size=10,  # Number of connections to maintain in the pool
    max_overflow=20,  # Number of connections beyond pool_size that can be opened
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=3600  # Recycle connections after 1 hour
)

def create_db_and_tables():
    """ 程式啟動時呼叫，自動建立所有資料表 """
    SQLModel.metadata.create_all(engine)

def get_session():
    """ Dependency: 讓每個請求都有獨立的資料庫連線 """
    with Session(engine) as session:
        yield session