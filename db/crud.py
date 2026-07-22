import random
from sqlalchemy import select
from db.db import AsyncSessionLocal, User, Quest

async def get_or_create_user(user_id: str):
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.user_id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(user_id=user_id)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
        return user
    
async def update_user(user_id: str, is_admin: bool):
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.user_id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            user.is_admin = is_admin
            await session.commit()
            await session.refresh(user)
            return user
        
        return None
    
    
    
async def get_quest(quest_id: int):
    async with AsyncSessionLocal() as session:
        return await session.get(Quest, quest_id)
    
async def get_random_quests():
    async with AsyncSessionLocal() as session:
        stmt = select(Quest.id)
        result = await session.execute(stmt)
        all_ids = list(result.scalars().all())
        
        random.shuffle(all_ids)
        return all_ids
    
async def create_quest(questions: list, audio: str = None, assignment: str = None):
    async with AsyncSessionLocal() as session:
        try:
            quest = Quest(
                audio=audio,
                assignment=assignment,
                questions=questions
            )
            session.add(quest)
            await session.commit()
            await session.refresh(quest)
            
            return quest
        except Exception as e:
            await session.rollback()
            print(f"Savol qo'shishda xatolik: {e}")
            return None