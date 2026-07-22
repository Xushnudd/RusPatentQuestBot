from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import Column, Integer, String, Boolean, JSON
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine("sqlite+aiosqlite:///db/botDataBase.db")

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, unique=True)
    is_premium = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    current_question_index = Column(Integer, default=0)
    
class Quest(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    audio = Column(String, nullable=True)
    assignment = Column(String, nullable=True)
    questions = Column(JSON, nullable=False)
    
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
        

