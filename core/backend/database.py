from . import constants as C
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, select, update, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

Base = declarative_base()
engine = create_async_engine("sqlite+aiosqlite:///main.db")
Session = sessionmaker(bind=engine)
session = Session()


class UsersTable(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    status = Column(String)
    message_id = Column(Integer)
    folder = relationship("FolderTable", back_populates="users")


class FolderTable(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    users = relationship("UsersTable", back_populates="folder")
    notes = relationship("NoteTable", back_populates="folder")


class NoteTable(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer)
    title = Column(String, nullable=False)
    content = Column(String)
    folder_id = Column(Integer, ForeignKey("folders.id"))
    folder = relationship("FolderTable", back_populates="notes")


async def set_status(user_id: int, new_status: str):
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        q = update(UsersTable).where(UsersTable.id == user_id).values(status=new_status)
        await session.execute(q)
        await session.commit()


async def get_status(user_id: int):
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        q = select(UsersTable.status).filter(UsersTable.id == user_id)
        result = await session.execute(q)
        status = result.fetchone()
        return status[0] if status else ""


async def set_buttons_message_id(user_id: int, new_message_id: str):
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        q = update(UsersTable).where(UsersTable.id == user_id).values(message_id=new_message_id)
        await session.execute(q)
        await session.commit()


async def get_buttons_message_id(user_id: int):
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        q = select(UsersTable.message_id).where(UsersTable.id == user_id)
        result = (await session.execute(q)).fetchone()
        print(result)
        return result[0] if result else None


async def set_note_message_id(note_id: int, new_message_id: str):
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        q = update(NoteTable).where(NoteTable.id == note_id).values(message_id=new_message_id)
        await session.execute(q)
        await session.commit()


async def get_note_message_id(note_id: int):
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        q = select(NoteTable.message_id).where(NoteTable.id == note_id)
        result = (await session.execute(q)).fetchone()
        return result[0] if result else None


async def get_notes_messages_ids(user_id: int):
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        q = select(NoteTable.message_id).join(FolderTable).filter(FolderTable.user_id == user_id)
        result = await session.execute(q)
        return [row[0] for row in result.fetchall()]


async def delete_folder(folder_id: int):
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        q = delete(FolderTable).where(FolderTable.id == folder_id)
        await session.execute(q)
        q = delete(NoteTable).where(NoteTable.folder_id == folder_id)
        await session.execute(q)
        await session.commit()


async def delete_note(note_id: int):
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        q = delete(NoteTable).where(NoteTable.id == note_id)
        await session.execute(q)
        await session.commit()


async def create_all_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
